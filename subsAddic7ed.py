from bs4 import BeautifulSoup
import requests
import re


def obterner_url_sub(serie, temporada, episodio, version):
	pnombresub = re.compile('^(' + serie + ') - (\d{2})x(\d{2}) - .+$')
	# html_busqueda = urllib.urlopen('http://www.addic7ed.com/search.php?search='+serie+'&Submit=Search').read()
	r = requests.get('http://www.addic7ed.com/search.php?search=' + serie + '&Submit=Search')
	soup = BeautifulSoup(r.text, 'lxml')

	encontrado = 0
	for a in soup.find(class_="tabel").find_all("a"):
		b = pnombresub.match(a.get_text())
		if b:
			if temporada == b.group(2) and episodio == b.group(3):
				encontrado = 1
				urlepisodio = "http://www.addic7ed.com/" + a.get("href")
				break

	if encontrado == 0:
		return None, None

	versionesaceptadas = versiones_aceptadas(version)

	r = requests.get(urlepisodio)
	soup = BeautifulSoup(r.text, 'lxml')
	urlhi = None

	for newsTitle in soup.find_all(class_="NewsTitle"):
		if not newsTitle.text.startswith("Version"):
			continue

		tabla = newsTitle.parent.parent
		trs = tabla.find_all("tr")
		if len(trs) < 2:
			continue

		tr = trs[1]
		newsdate = tr.find(class_="newsDate")
		if newsdate is None:
			continue
		#print newsTitle.text
		#print "->" + newsdate.text

		versionencontrada = 0
		estaversion = newsTitle.text[8:].split(",")[0].lower()
		for buscar in versionesaceptadas:
			if estaversion.find(buscar) > -1 or newsdate.text.lower().find(buscar) > -1:
				versionencontrada = 1
				break
		if versionencontrada == 0:
			continue

		# Buscamos si es HI e idioma
		hearingimpaired = 0
		for img in tabla.find_all("img"):
			title = img.get("title")
			if title is None:
				continue
			if title.find("Hearing Impaired") > -1:
				hearingimpaired = 1
				break

		for language in tabla.find_all(class_="language"):
			buttondownloads = language.parent.find_all(class_="buttonDownload")
			if len(buttondownloads) < 1:
				continue
			buttondownload = buttondownloads[-1]  # Ultimo elemento

			urlsub = buttondownload.get("href")
			urlsub = "http://www.addic7ed.com" + urlsub

			if language.text.lower().find("english") > -1:
				if hearingimpaired == 1:
					urlhi = urlsub
				else:
					return urlsub, urlepisodio

	return urlhi, urlepisodio


def versiones_aceptadas(entrada):
	version = entrada.lower()
	versiones = list()
	if version == "dimension" or version == "lol" or version == "sys":
		versiones.append("dimension")
		versiones.append("lol")
		versiones.append("sys")
	elif version == "immerse" or version == "xii" or version == "asap":
		versiones.append("immerse")
		versiones.append("xii")
		versiones.append("asap")
	elif version == "orenji" or version == "fqm":
		versiones.append("orenji")
		versiones.append("fqm")
	else:
		versiones.append(version)
	return versiones


serie = "Grey's Anatomy"
temporada = "12"
episodio = "22"
version = "DIMENSION"
ruta = "/Users/Alex/Movies/Greys.Anatomy.S12E22.HDTV.mkv"

k = ruta.rfind(".")
rutaSub = ruta[:k] + ".srt"

urlSub, urlEpisodio = obterner_url_sub(serie, temporada, episodio, version)


headers = {"Referer": urlEpisodio}
r = requests.get(urlSub, headers=headers)
with open(rutaSub, "wb") as code:
	code.write(r.content)
