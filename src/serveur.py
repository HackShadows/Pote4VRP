from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import legacy_cgi

from typing import Callable

import time
from webbrowser import open_new_tab
from threading import Thread






class ServeurVRP(SimpleHTTPRequestHandler) :


	def __init__(self, process_function, *args, **kwargs) :
		self.process_function = process_function
		super().__init__(*args, **kwargs)



	def do_GET(self) :
		if self.path == '/' :
			# Serve the index.html file
			self.serve_file('interface_utilisateur/index.html')
		elif self.path.endswith('.js') :
			# Serve the script.js file
			self.serve_file('interface_utilisateur/script.js')
		elif self.path.endswith('.css'): 
			# Serve the style.css file
			self.serve_file('interface_utilisateur/static/css/style.css')
		elif self.path.endswith('.png') :
			self.serve_file(self.path.lstrip('/'))
		elif self.path == '/success' :
			self.serve_file('interface_utilisateur/success.html')
		else :
			self.serve_unknown_page(self.path.split('/')[-1])



	def do_POST(self) :
		if self.path == '/process' :
			# Handle file upload
			form = legacy_cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={
					'REQUEST_METHOD': 'POST',
					'CONTENT_TYPE': self.headers['Content-Type'],
				}
			)
			page = self.process_data([form[key] for key in form.keys() if key.startswith("file_")])

			with open("interface_utilisateur/success.html", "w") as f :
				f.write(page)

			self.send_response(301)  # 302 Found (Redirect)
			self.send_header("Location", "/success")
			self.end_headers()
		else :
			self.serve_unknown_page(self.path.split('/')[-1])



	def serve_file(self, file_path):
		try:
			with open(file_path, 'rb') as f:
				content = f.read()
			self.send_response(200)
			if file_path.endswith('.html'):
				self.send_header("Content-type", "text/html")
			elif file_path.endswith('.js'):
				self.send_header("Content-type", "application/javascript")
			elif file_path.endswith('.css'):
				self.send_header("Content-type", "text/css")
			elif file_path.endswith('.png'):
				self.send_header("Content-type", "image/png")
			self.end_headers()
			self.wfile.write(content)
		except FileNotFoundError:
			self.serve_unknown_page(file_path.split('/')[-1])
	


	def serve_unknown_page(self, url) :
		self.send_response(404)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		with open("interface_utilisateur/not_found.html", "r") as f :
			self.wfile.write((f % url).encode())



	def process_data(self, files) :
		print("Processing data...")
		
		download = list()
		content = ""
		for file in files :
			try :
				d, c = self.process_function(file.filename, file.file.read())
				download.append(d)
				content += c
			except Exception as e:
				content += """<div class="erreur"><h2><Erreur lors du traitement des données de %s</h2><code>%s</code></div>""" % (file.filename, repr(e))

		with open("interface_utilisateur/result.html", "r") as f :
			result = f.read() % content

		print("Data processing complete.")
		return result





def lancer_serveur(fonction_traitement :Callable[[legacy_cgi.FieldStorage], None], port :int = 8080) -> str :
	addresse_serveur = "localhost", port
	url = "http://%s:%s" % addresse_serveur

	instantiate = lambda *args,**kwargs : ServeurVRP(fonction_traitement, *args, **kwargs)
	try:
		thread = Thread(target = lambda : time.sleep(3) or open_new_tab(url))
		thread.start()
		with HTTPServer(addresse_serveur, instantiate) as serveur_web :
			serveur_web.serve_forever()
	except KeyboardInterrupt:
		pass
	
	thread.join()
	return url
