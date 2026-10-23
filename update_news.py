import json, urllib.request, xml.etree.ElementTree as ET, email.utils
from pathlib import Path
from datetime import datetime, timezone
feeds=[('Le Monde Informatique','https://www.lemondeinformatique.fr/flux-rss/thematique/toutes-les-actualites/rss.xml','Informatique'),('CERT-FR','https://www.cert.ssi.gouv.fr/alerte/feed/','Cybersécurité')]
target=Path('news.json')
try: previous=json.loads(target.read_text(encoding='utf-8-sig'))
except (OSError,ValueError): previous={'articles':[]}
articles=[];sources=[]
for name,url,category in feeds:
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Portfolio-Meziane-RSS/1.0'})
  with urllib.request.urlopen(request,timeout=25) as response: root=ET.fromstring(response.read())
  current=[]
  for item in root.findall('.//item')[:25]:
   link=(item.findtext('link') or '').strip()
   title=(item.findtext('title') or '').strip()
   if title and link.startswith(('https://','http://')):current.append(dict(title=title,url=link,date=item.findtext('pubDate') or '',source=name,category=category))
  if not current:raise ValueError('Empty feed')
  articles.extend(current);sources.append(dict(source=name,ok=True))
 except Exception as error:
  print(name+': '+str(error))
  articles.extend(a for a in previous.get('articles',[]) if a.get('source')==name)
  sources.append(dict(source=name,ok=False))
def timestamp(article):
 try:return email.utils.parsedate_to_datetime(article['date']).timestamp()
 except Exception:return 0
articles.sort(key=timestamp,reverse=True)
# Fail the job if both sources fail; preserve the previous published feed.
if not any(source['ok'] for source in sources):raise SystemExit('All sources unavailable; preserving previous data')
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(dict(articles=articles,sources=sources,updatedAt=datetime.now(timezone.utc).isoformat()),ensure_ascii=False),encoding='utf-8-sig')
print(str(len(articles))+' articles saved')

