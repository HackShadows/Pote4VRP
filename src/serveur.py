from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import legacy_cgi
import mimetypes
import base64, enum, hashlib, os, random, struct
from queue import Queue
from zipfile import ZipFile

from jinja2 import Environment, FileSystemLoader, select_autoescape

from typing import Any, Callable, IO, Optional, Self
from pathlib import Path


from threading import Thread
import time
import webbrowser



mimetypes.add_type("text/plain", ".vrp")







GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"





class Frame : # Called a Frame since a "message" is comprised of (or fragmented into) Frames



	class Opcode(enum.IntEnum) :
		CONTINUATION     = 0b_0000
		TEXT             = 0b_0001
		BINARY           = 0b_0010
		RSV3             = 0b_0011
		RSV4             = 0b_0100
		RSV5             = 0b_0101
		RSV6             = 0b_0110
		RSV7             = 0b_0111
		CONNECTION_CLOSE = 0b_1000
		PING             = 0b_1001
		PONG             = 0b_1010
		CONTROL_RSVB     = 0b_1011
		CONTROL_RSVC     = 0b_1100
		CONTROL_RSVD     = 0b_1101
		CONTROL_RSVE     = 0b_1110
		CONTROL_RSVF     = 0b_1111

	class CloseCode(enum.IntEnum) :
		NORMAL_CLOSURE             = 1000
		GOING_AWAY                 = 1001
		PROTOCOL_ERROR             = 1002
		UNSUPPORTED_DATA           = 1003
		NO_STATUS_RCVD             = 1005
		ABNORMAL_CLOSURE           = 1006
		INVALID_FRAME_PAYLOAD_DATA = 1007
		POLICY_VIOLATION           = 1008
		MESSAGE_TOO_BIG            = 1009
		MANDATORY_EXT              = 1010
		INTERNAL_SERVER_ERROR      = 1011
		TLS_HANDSHAKE              = 1015





	__slots__ = "final", "reserved1", "reserved2", "reserved3", "opcode", "mask", "payload"


	def __init__(self, final     :bool
	                 , opcode    :Opcode
	                 , payload   :Optional[list]       = None
	                 , mask      :Optional[bytes|bool] = None
	                 , reserved1 :bool                 = False
	                 , reserved2 :bool                 = False
	                 , reserved3 :bool                 = False) :

		self.final     = final
		self.reserved1 = reserved1
		self.reserved2 = reserved2
		self.reserved3 = reserved3
		self.opcode    = opcode
		match mask :
			case bytes()      : self.mask = mask
			case None | False : self.mask = None
			case True         : self.mask = struct.pack(">I", random.randrange(1 << 32))
		self.payload = bytes() if payload is None else payload
	


	def __repr__(self) -> str :
		return (
			f"Frame(final: {self.final}"
			f", reserved: {int(self.reserved1)}{int(self.reserved1)}{int(self.reserved1)}"
			f", opcode: {self.opcode.name}"
			f", mask: {self.mask}"
			f", payload: {self.payload if len(self.payload) < 30 else str(self.payload)[:30]+'...'})"
		)



	@classmethod
	def from_bytes(cls, source    :bytes|bytearray|IO[bytes]
			  , *, offset :Optional[int]             = 0) -> Self :

		if isinstance(source, (bytes, bytearray)) :
			header = source[offset : offset+2]
			offset += 2
		else : header = source.read(2)

		final  =       bool(header[0] & 0b_1000_0000)
		rsv1   =       bool(header[0] & 0b_0100_0000)
		rsv2   =       bool(header[0] & 0b_0010_0000)
		rsv3   =       bool(header[0] & 0b_0001_0000)
		opcode = cls.Opcode(header[0] & 0b_0000_1111)

		masked = bool(header[1] & 0x80)
		length = header[1] & 0x7F

		if isinstance(source, (bytes, bytearray)) :
			if length == 0x7F :
				payload_length = struct.unpack(">Q", source[offset : offset+8])
				offset += 8
			elif length == 0x7E :
				payload_length = struct.unpack(">H", source[offset : offset+2])
				offset += 2
			else : payload_length = length

			if masked :
				mask = source[offset : offset+4]
				offset += 4
			else : mask = None

			payload = source[offset : offset + payload_length]
		else :
			if   length == 0x7F : payload_length = struct.unpack(">Q", source.read(8))
			elif length == 0x7E : payload_length = struct.unpack(">H", source.read(2))
			else                : payload_length = length

			mask = None if masked is False else source.read(4)

			payload = source.read(payload_length)

		if masked :
			payload = bytes(b ^ mask[i%4] for i, b in enumerate(payload))


		return cls(final, opcode, payload, mask, rsv1, rsv2, rsv3)



	def __bytes__(self) -> bytes :
		return self.to_bytes()



	def to_bytes(self, *, out :Optional[IO[bytes]] = None) -> bytes|None :
		masked = self.mask is not None

		payload_length = len(self.payload)
		if payload_length > 0xFFFF :
			length_info = 0x7F
			length = struct.pack(">Q", payload_length)
		elif payload_length >= 0x7E :
			length_info = 0x7E
			length = struct.pack(">H", payload_length)
		else :
			length_info = payload_length
			length = bytes()

		if out is None :
			result = bytearray(2 + len(length) + 4*masked + payload_length)

			result[0] = (self.final << 7) | (self.reserved1 << 6) | (self.reserved2 << 5) | (self.reserved3 << 4) | int(self.opcode)
			result[1] = (masked << 7) | length_info

			offset = 2+len(length)
			result[2 : offset] = length

			if masked :
				result[offset : offset+4] = self.mask
				offset += 4

				result[offset : ] = bytes(b ^ self.mask[i%4] for i, b in enumerate(self.payload))
			else : result[offset : ] = self.payload

			return bytes(result)

		else :
			out.write(struct.pack("B", (self.final << 7) | (self.reserved1 << 6) | (self.reserved2 << 5) | (self.reserved3 << 4) | int(self.opcode)))
			out.write(struct.pack("B", (masked << 7) | length_info))
			out.write(length)
			if masked :
				out.write(self.mask)
				out.write(bytes(b ^ self.mask[i%4] for i, b in enumerate(self.payload)))
			else : out.write(self.payload)

			return None







class WebSocket :



	__slots__ = "rfile", "wfile", "closed_first"


	def __init__(self, rfile, wfile) :
		self.rfile = rfile
		self.wfile = wfile
		self.closed_first = False



	def fileno(self) :
		return self.rfile.fileno()



	def _close(self, payload :bytes) :
		self.send(Frame(True, Frame.Opcode.CONNECTION_CLOSE, payload))
	
	def close(self, code :Optional[Frame.CloseCode] = Frame.CloseCode.NORMAL_CLOSURE) :
		self.closed_first = True
		self._close(struct.pack(">H", int(code)))



	def detach(self) :
		self.rfile = self.wfile = None



	def ping(self) :
		self.send(Frame(True, Frame.Opcode.PING))

	def pong(self) :
		self.send(Frame(True, Frame.Opcode.PONG))



	# TODO: On peut probablement drastiquement réduire la taille de tout ça
	def receive(self) -> Optional[str|bytes] :
		opcode = None
		buffer = bytearray()



		while True :
			frame = Frame.from_bytes(self.rfile)
			print(repr(frame))

			if frame.mask is None :
				self.close(Frame.CloseCode.PROTOCOL_ERROR)



			if frame.final :
				match frame.opcode :

					case Frame.Opcode.CONTINUATION :
						match opcode :
							case None :
								self.close(Frame.CloseCode.PROTOCOL_ERROR) # Did not receive initial frame

							case Frame.Opcode.TEXT :
								buffer.extend(frame.payload)
								try :
									return buffer.decode("utf-8")
								except UnicodeDecodeError :
									self.close(Frame.CloseCode.INVALID_FRAME_PAYLOAD_DATA)

							case Frame.Opcode.BINARY | Frame.Opcode.RSV5 :
								buffer.extend(frame.payload)
								return bytes(buffer)

							case _ :
								raise NotImplementedError # Continuation of other Frame.Opcode


					case Frame.Opcode.TEXT :
						try :
							return frame.payload.decode("utf-8")
						except UnicodeDecodeError:
							self.close(Frame.CloseCode.INVALID_FRAME_PAYLOAD_DATA)


					case Frame.Opcode.BINARY | Frame.Opcode.RSV5 :
						return frame.payload


					case Frame.Opcode.CONNECTION_CLOSE :
						if not self.closed_first :
							self._close(frame.payload)
						self.detach()
						return


					case Frame.Opcode.PING :
						self.pong()


					case Frame.Opcode.PONG :
						pass


					case _ :
						self.close(Frame.CloseCode.PROTOCOL_ERROR)



			else :
				match frame.opcode :

					case Frame.Opcode.CONTINUATION :
						match opcode :
							case None :
								self.close(Frame.CloseCode.PROTOCOL_ERROR) # Did not receive initial frame

							case Frame.Opcode.TEXT :
								buffer.extend(frame.payload)

							case Frame.Opcode.BINARY | Frame.Opcode.RSV5 :
								buffer.extend(frame.payload)

							case _ :
								raise NotImplementedError # Continuation of other Frame.Opcode


					case Frame.Opcode.TEXT :
						opcode = Frame.Opcode.TEXT
						buffer = bytearray(frame.payload)


					case Frame.Opcode.BINARY | Frame.Opcode.RSV5 :
						opcode = Frame.Opcode.TEXT
						buffer = bytearray(frame.payload)


					case _ :
						raise NotImplementedError # Start of other Frame.Opcode



	def send(self, data :Frame|str|bytes) :
		match data :
			case Frame() : frame = data
			case str()   : frame = Frame(True, Frame.Opcode.TEXT  , data.encode("utf-8"))
			case bytes() : frame = Frame(True, Frame.Opcode.BINARY, data)
			case _ :
				raise NotImplementedError
		frame.to_bytes(out=self.wfile)






class Tâche :

	_ID_TACHES = 0

	class Etat(enum.Enum) :
		EN_COURS = 0
		SUCCES = 1
		ERREUR = 2
	
	__slots__ = "id", "nom", "état", "données", "message_erreur"

	def __init__(self, nom :str, données :Any) :
		self.id = self._ID_TACHES
		self.nom = nom
		self.état = self.Etat.EN_COURS
		self.données = données
		self.message_erreur = ""

		self.__class__._ID_TACHES += 1


class Client :

	class State(enum.Enum) :
		MAIN_PAGE  = 0
		PROCESSING = 1
		FINISHED   = 2

	__slots__ = "état", "tâches", "queue"

	def __init__(self, état :State) :
		self.état   = état
		self.tâches = None
		self.queue  = None
	

	def id_groupe_tâches(self) -> str|None :
		if self.tâches is None :
			return None
		return f"{id(self)}_{self.tâches[0].id}"

	def id_tâche(self, index :int) -> str|None :
		if self.tâches is None or not(0 <= index < len(self.tâches)) :
			return None
		return f"{id(self)}_{self.tâches[index].id}_{self.tâches[index].nom}"


	def préparer_traitement(self, tâches :list[Tâche]) :
		self.tâches = tâches
		self.queue = Queue()
		self.état = self.State.PROCESSING
	
	def notifier(self, tâche_id :int) :
		self.queue.put(tâche_id)

	def cloturer_traitement(self) :
		self.état = self.State.FINISHED
	
	def réinitialiser(self, état :State) :
		self.état   = état
		self.tâches = None
		self.queue  = None






class TraitementRequêteVRP(BaseHTTPRequestHandler) :


	@staticmethod
	def is_path_safe(base_path :Path, test_path :Path) -> bool :
		base_path = base_path.resolve()
		test_path = (base_path / test_path).resolve()
		return test_path.is_relative_to(base_path)




	def opening_handshake(self) -> bool :

		def error(code :int, reason :str) :
			self.send_response(code)
			self.log_error(f"Could not open handshake : {reason}")


		if self.request_version != "HTTP/1.1" :
			error(505, "requested version is not HTTP/1.1")
			return False
		self.protocol_version = "HTTP/1.1"

		if "Upgrade" not in self.headers.get("Connection")  :
			error(400, f"\"Connection\" = \"{self.headers.get('Connection')}\"")
			return False
		if self.headers.get("Upgrade") != "websocket":
			error(400, f"\"Connection\" = \"{self.headers.get('Upgrade')}\"")
			return False
		if self.headers.get("Sec-WebSocket-Version") != "13" :
			error(400, f"\"Connection\" = \"{self.headers.get('Sec-WebSocket-Version')}\"")
			return False

		key = self.headers.get("Sec-WebSocket-Key")
		if key is None :
			error(400, "Sec-WebSocket-Key is none")
			return False


		accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
		self.send_response(101)
		self.send_header("Upgrade", "websocket")
		self.send_header("Connection", "Upgrade")
		self.send_header("Sec-WebSocket-Accept", accept)
		self.end_headers()

		self.websocket = WebSocket(self.rfile, self.wfile)
		return True



	def listen(self) :
		tâche_index = self.client.queue.get()
		while tâche_index is not None :
			tâche = self.client.tâches[tâche_index]
			self.websocket.send(f"{self.client.id_tâche(tâche_index)}:{int(tâche.état == Tâche.Etat.SUCCES)}:{tâche.message_erreur}")
			tâche_index = self.client.queue.get()
		self.client.cloturer_traitement()
		self.websocket.close()





	def do_GET(self) :
		_, _, path, _, query, _ = urlparse(self.path) # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>


		self.client = self.server.clients.get(None)
		if self.client is None :
			self.client = self.server.clients[None] = Client(Client.State.MAIN_PAGE)


		match self.client.état :
			case Client.State.MAIN_PAGE :
				if path == "/" and self.serve_main_page()  : return
			case Client.State.PROCESSING :
				if path     ==     "/"          and self.serve_processing()   : return
				if path.startswith("/resultat") and self.serve_résultat(path) : return
				if path     ==     "/ws"        and self.handle_websocket()   : return
			case Client.State.FINISHED :
				if path  ==  "/" and not query                   and self.serve_résultats()    : return
				if path  ==  "/" and query == "redirect=accueil" and self.redirect_accueil()   : return
				if path.startswith("/resultat")                 and self.serve_résultat(path) : return


		if path.endswith(".js" ) and self.serve_javascript(path) : return
		if path.endswith(".css") and self.serve_css(path)        : return

		self.serve_unknown_page(path)



	def serve_main_page(self) -> bool :
		template = self.server.environnement.get_template("accueil.html")
		self.serve_content(".html", template.render(CONFIG = {"page" : "accueil"}).encode())
		return True

	def redirect_accueil(self) -> bool :
		for file in os.listdir("data/out") :
			if os.path.isfile(f"data/out/{file}") :
				os.unlink(f"data/out/{file}")
		self.client.réinitialiser(Client.State.MAIN_PAGE)
		return self.serve_main_page()
	

	def serve_processing(self) -> bool :
		template = self.server.environnement.get_template("chargement.html")
		config = {
			"page" : "chargement",
			"taches" : [{
				"id" : self.client.id_tâche(i),
				"nom" : tâche.nom,
				"état" : tâche.état.name,
				"message_erreur" : tâche.message_erreur,
			} for i, tâche in enumerate(self.client.tâches)]
		}
		self.serve_content(".html", template.render(CONFIG = config).encode())
		return True


	def serve_résultats(self) -> bool :
		template = self.server.environnement.get_template("resultats.html")
		config = {
			"page" : "resultats",
			"taches" : [{
				"id" : self.client.id_tâche(i),
				"nom" : tâche.nom,
				"état" : tâche.état.name,
				"message_erreur" : tâche.message_erreur,
			} for i, tâche in enumerate(self.client.tâches)]
		}
		self.serve_content(".html", template.render(CONFIG = config).encode())
		return True



	def serve_résultat(self, path :str) -> bool :
		if path.count("/") == 1 :
			if path != "/resultats" :
				return False
			self.serve_file(Path(f"data/out/{self.client.id_groupe_tâches()}.zip"))

		else :
			_, head, rel_path = path.split('/', 2)
			if head != "resultat" or not path.endswith(('.svg', '.vrp')) :
				return False

			base_path = Path("data/out")
			if self.is_path_safe(base_path, rel_path) :
				self.serve_file(base_path / rel_path)
			else :
				self.send_reponse(404)
		return True



	def handle_websocket(self) -> bool :
		if self.opening_handshake() :
			self.listen()
		return True



	def serve_javascript(self, path :str) -> bool :
		rel_path = path.lstrip('/')
		base_path = Path("interface_utilisateur/static/javascript")
		if self.is_path_safe(base_path, rel_path) :
			self.serve_file(base_path / rel_path)
		else : self.send_response(404)
		return True

	def serve_css(self, path :str) -> bool :
		rel_path = path.lstrip('/')
		base_path = Path("interface_utilisateur/static/css")
		if self.is_path_safe(base_path, rel_path) :
			self.serve_file(base_path / rel_path)
		else : self.send_response(404)
		return True





	def do_POST(self) :
		self.client = self.server.clients.get(None)
		if self.client is None :
			self.client = self.server.clients[None] = Client(Client.State.MAIN_PAGE)


		form = legacy_cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={
				'REQUEST_METHOD': 'POST',
				'CONTENT_TYPE': self.headers['Content-Type'],
			}
		)


		match self.client.état :
			case Client.State.MAIN_PAGE :
				if self.path == "/" and self.handle_upload(form) : return
			case Client.State.PROCESSING :
				pass
			case Client.State.FINISHED :
				pass

		self.serve_unknown_page(self.path)
	


	def handle_upload(self, formulaire :legacy_cgi.FieldStorage) -> bool :

		fichiers = [formulaire[key] for key in formulaire.keys() if key.startswith("fichier_")]
		if not fichiers : return False

		tâches = [Tâche(fichier.filename.rsplit('.', 1)[0], fichier.file.read()) for fichier in fichiers]
		print(f"GOT {len(fichiers)} files : ", ", ".join(file.filename for file in fichiers))
		print("Processing data...")

		self.client.préparer_traitement(tâches)
		thread = Thread(target=self.process, args=(self.server.traitement, self.client))
		thread.start()

		self.send_response(200)
		self.end_headers()
		return True



	def serve_content(self, ext :str, content :bytes) :
		mimetype = mimetypes.types_map.get(ext, None)
		if mimetype is None :
			self.log_error(f"The mimetype for '{ext}' is unknown")
			self.send_response(500)
		else :
			self.send_response(200)
			self.send_header("Content-type", mimetype)
			self.end_headers()
			self.wfile.write(content)



	def serve_file(self, file_path :Path) :
		if file_path.exists() :
			self.serve_content(file_path.suffix, file_path.read_bytes())
		else : self.send_response(404)
	


	def serve_unknown_page(self, path :str|Path) :
		self.send_response(404)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		template = self.server.environnement.get_template("erreur.html")
		self.wfile.write(template.render(CONFIG = {"page" : "erreur", "erreur" : "Erreur 404 Not Found", "message_erreur" : f"Chemin non trouvé : {path}"}).encode())
	



	@staticmethod
	def process(traitement :Callable[[str, bytes], Optional[str]], client :Client) :
		for i, tâche in enumerate(client.tâches) :
			erreur = traitement(client.id_tâche(i), tâche.données)
			if erreur is None :
				tâche.état = Tâche.Etat.SUCCES
			else :
				tâche.état = Tâche.Etat.ERREUR
				tâche.message_erreur = erreur
			client.notifier(i)

		with ZipFile(f"data/out/{client.id_groupe_tâches()}.zip", 'w') as vrpzip :
			for i, tâche in enumerate(client.tâches) :
				if tâche.état is Tâche.Etat.SUCCES :
					vrpzip.write(f"data/out/{client.id_tâche(i)}.vrp")

		client.notifier(None)







class ServeurVRP(ThreadingHTTPServer) :





	def __init__(self, addresse               :tuple[str, int]
	                 , handler                :BaseHTTPRequestHandler
	                 , fonction_de_traitement :Callable[[str, IO[str]], tuple[str, Optional[str]]]) :

		for file in os.listdir("data/out") :
			if os.path.isfile(f"data/out/{file}") :
				os.unlink(f"data/out/{file}")

		self.traitement    = fonction_de_traitement
		self.clients       = dict()
		self.environnement = Environment(loader=FileSystemLoader("interface_utilisateur/templates"), autoescape=select_autoescape())

		super().__init__(addresse, handler)





def lancer_serveur(fonction_traitement :Callable[[str, bytes], Optional[str]], port :int = 8080) -> str :
	addresse_serveur = "localhost", port
	url = "http://%s:%s" % addresse_serveur


	def ouvrir_navigateur() :
		time.sleep(1)
		webbrowser.open_new_tab(url)


	thread = Thread(target=ouvrir_navigateur)
	try:
		with ServeurVRP(addresse_serveur, TraitementRequêteVRP, fonction_traitement) as serveur_web :
			thread.start()
			print("serve 2")
			serveur_web.serve_forever()
	except KeyboardInterrupt:
		pass
	thread.join()


	return url
