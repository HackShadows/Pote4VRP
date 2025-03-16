from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import time
import cgi





NOT_FOUND_PAGE = """\
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>404 Not Found</title>
	<style>
		body {{
			display: flex;
			flex-flow: column nowrap;
			justify-content: center;
			align-items: center;
			height: 100vh;
			margin: 0;
		}}
		h1 {{
			font-size: 28px;
			font-weight: 700;
			line-height: 34px;
			margin: 0 auto;
		}}
	</style>
</head>
<body>
	<h1>404 "{}" Was Not Found</h1>
</body>
</html>\
"""





class ServeurVRP(SimpleHTTPRequestHandler) :


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
		else :
			self.serve_unknown_page(self.path.split('/')[-1])



	def do_POST(self) :
		if self.path == '/process' :
			# Handle file upload
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD': 'POST',
				         'CONTENT_TYPE': self.headers['Content-Type'],
				         })
			self.process_data(form.getlist())

			# Serve the loading page
			self.serve_file('ui/loading.html')

			# Serve the result page
			self.serve_file('ui/result.html')
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
			self.end_headers()
			self.wfile.write(content)
		except FileNotFoundError:
			self.serve_unknown_page(file_path.split('/')[-1])
	


	def serve_unknown_page(self, url) :
		self.send_response(404)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(NOT_FOUND_PAGE.format(url).encode())



	def process_data(self, files):
		# Implement your data processing logic here
		print("Processing data...")
		with open("TEMP.txt", "w") as f :
			for file in files :
				print(repr(files), file=f, end="\n\n\n\n")
		
		for file in files :
			self.process_function(file)

		print("Data processing complete.")





def lancer_serveur(port :int = 8080, fonction_traitement :Callable[[cgi.FieldStorage], None]) -> str :
	addresse_serveur = "localhost", port
	url = "http://%s:%s" % addresse_serveur

	try:
		with HTTPServer(addresse_serveur, ServeurVRP) as serveur_web :
			print(f"Le serveur à démarré à {url}")
			serveur_web.process_function = fonction_traitement
			serveur_web.serve_forever()
	except KeyboardInterrupt:
		pass
	
	print("Serveur terminé")
	return url
