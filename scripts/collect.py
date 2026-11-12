import csv, re, pathlib, hashlib, json
from datetime import date
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'; RAW.mkdir(parents=True,exist_ok=True)
START='2023-01-01'; END='2026-11-12'
SOURCES=[('OpenAI','company','https://deploymentsafety.openai.com/'),('Anthropic','company','https://www.anthropic.com/system-cards'),('Google','company','https://deepmind.google/models/model-cards/'),('Meta','company','https://github.com/meta-llama/llama-models'),('Moonshot AI','company','https://github.com/MoonshotAI'),('DeepSeek','company','https://deepseek.com/en/transparency/'),('MIT','taxonomy','https://airisk.mit.edu/risks'),('Epoch AI','benchmark','https://epoch.ai/benchmarks/use-this-data'),('METR','independent','https://metr.org/evaluations/'),('METR','independent','https://metr.org/time-horizons/'),('UK AISI','independent','https://www.aisi.gov.uk/frontier-ai-trends-report')]
S=requests.Session(); S.headers['User-Agent']='DS320 academic data collection/1.0'
def get(url):
 r=S.get(url,timeout=60); r.raise_for_status(); return r

def save(url,path):
 r=get(url); path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(r.content); return hashlib.sha256(r.content).hexdigest()

def main():
 errors=[]; links=[]
 try:
  p=RAW/'epoch'/'all_ai_models.csv'; save('https://epoch.ai/data/all_ai_models.csv',p)
  df=pd.read_csv(p,low_memory=False)
  names={'OpenAI':r'\bopenai\b','Anthropic':r'\banthropic\b','Google':r'\bgoogle\b|\bdeepmind\b','Meta':r'\bmeta\b|\bfacebook\b','Moonshot AI':r'\bmoonshot\b','DeepSeek':r'\bdeepseek\b'}
  org=df['Organization'].fillna('').astype(str); dates=pd.to_datetime(df['Publication date'],errors='coerce',utc=True)
  df['matched_companies']=org.map(lambda x:';'.join(k for k,v in names.items() if re.search(v,x,re.I)))
  out=df[df.matched_companies.ne('') & dates.between(pd.Timestamp(START,tz='UTC'),pd.Timestamp(END,tz='UTC'))].copy()
  out.to_csv(ROOT/'data'/'processed'/'epoch_six_companies.csv',index=False)
  # Broad metadata universe: manually screen domains, joint developers and versions before analysis.
  print('Epoch candidate records:',len(out))
 except Exception as e: errors.append({'source':'Epoch models','error':str(e)})
 for i,(org,kind,url) in enumerate(SOURCES):
  try:
   r=get(url); p=RAW/'indexes'/f'{i:02d}_{org.replace(" ","_")}.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(r.content)
   soup=BeautifulSoup(r.content,'html.parser')
   for a in soup.select('a[href]'):
    href=urljoin(r.url,a['href']); label=' '.join(a.stripped_strings)
    if urlparse(href).scheme not in ('http','https'): continue
    if re.search(r'card|report|evaluat|benchmark|dataset|download|\.pdf|\.csv|\.zip|kimi|llama|deepseek|claude|gemini|gpt|risk|taxonomy|spreadsheet',label+' '+href,re.I):
     links.append({'organization':org,'source_type':kind,'index_url':url,'title':label,'url':href,'status':'candidate_unreviewed'})
  except Exception as e: errors.append({'source':url,'error':str(e)})
 pd.DataFrame(links,columns=['organization','source_type','index_url','title','url','status']).drop_duplicates().to_csv(ROOT/'data'/'processed'/'discovered_links.csv',index=False)
 # Download only explicitly reviewed URLs in the manifest; indexes are not model-specific reports.
 with (ROOT/'data'/'source_manifest.csv').open(newline='',encoding='utf-8') as f:
  for row in csv.DictReader(f):
   if row['download']!='yes': continue
   try:
    url=row['url']; ext='.pdf' if url.lower().endswith('.pdf') else '.html'; p=RAW/'documents'/f"{row['source_id']}{ext}"
    digest=save(url,p); row['local_path']=str(p.relative_to(ROOT)); row['sha256']=digest
   except Exception as e: errors.append({'source':row['url'],'error':str(e)})
 (RAW/'collection_errors.json').write_text(json.dumps(errors,indent=2))
 print('Discovery links:',len(links),'Errors:',len(errors))
if __name__=='__main__': main()

