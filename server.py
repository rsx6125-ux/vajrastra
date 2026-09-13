"""VAJRASTRA local demonstration server. Python 3.10+, standard library only."""
import base64
import binascii
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import urllib.request
from datetime import datetime, timezone
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('VAJRASTRA_DATA', ROOT / 'data'))
PORT = int(os.environ.get('PORT', '8000'))
LOCK = threading.Lock()
CATALOG = [
 {'id':'income','name':'Income certificate','hi':'आय प्रमाण पत्र','te':'ఆదాయ ధృవీకరణ పత్రం','category':'Certificates','icon':'file','description':'Prepare proof of income for education and welfare applications.','documents':['Identity proof','Address proof','Income evidence'],'fee':35,'days':'7–15','keywords':['income','आय','ఆదాయ']},
 {'id':'residence','name':'Residence certificate','hi':'निवास प्रमाण पत्र','te':'నివాస ధృవీకరణ పత్రం','category':'Certificates','icon':'home','description':'Get your details ready for a residence certificate.','documents':['Identity proof','Address proof'],'fee':35,'days':'7–15','keywords':['residence','address','నివాస','निवास']},
 {'id':'pension','name':'Pension renewal','hi':'पेंशन नवीनीकरण','te':'పెన్షన్ పునరుద్ధరణ','category':'Welfare','icon':'heart','description':'A guided renewal for senior citizens and pension holders.','documents':['Identity proof','Pension reference','Life certificate'],'fee':0,'days':'15–30','keywords':['pension','senior','పెన్షన్','पेंशन']},
 {'id':'disability','name':'Disability certificate','hi':'दिव्यांगता प्रमाण पत्र','te':'వైకల్య ధృవీకరణ పత్రం','category':'Certificates','icon':'access','description':'Prepare your application and medical assessment documents.','documents':['Identity proof','Photograph','Medical report'],'fee':0,'days':'15–30','keywords':['disability','disabled','వైకల్య','దివ్యాంగ','दिव्यांग']},
 {'id':'health','name':'Healthcare enrollment','hi':'स्वास्थ्य योजना नामांकन','te':'ఆరోగ్య పథకం నమోదు','category':'Healthcare','icon':'plus','description':'Organize the information needed to apply for health coverage.','documents':['Identity proof','Address proof','Family details'],'fee':0,'days':'7–30','keywords':['health','hospital','ఆరోగ్య','स्वास्थ्य']},
 {'id':'license','name':'License renewal','hi':'लाइसेंस नवीनीकरण','te':'లైసెన్స్ పునరుద్ధరణ','category':'Renewals','icon':'card','description':'Prepare an existing license for the authorized renewal process.','documents':['Identity proof','Existing license','Address proof'],'fee':200,'days':'15–30','keywords':['license','licence','లైసెన్స్','लाइसेंस']},
 {'id':'grievance','name':'File a grievance','hi':'शिकायत दर्ज करें','te':'ఫిర్యాదు నమోదు','category':'Grievances','icon':'message','description':'Write down a service issue and the resolution you need.','documents':[],'fee':0,'days':'7–30','keywords':['grievance','complaint','problem','ఫిర్యాదు','शिकायत']},
 {'id':'benefit','name':'Welfare scheme application','hi':'कल्याण योजना आवेदन','te':'సంక్షేమ పథకం దరఖాస్తు','category':'Welfare','icon':'spark','description':'Prepare a new application for a welfare scheme.','documents':['Identity proof','Address proof','Income evidence'],'fee':0,'days':'15–30','keywords':['scheme','benefit','welfare','పథకం','योजना']},
]

def now(): return datetime.now(timezone.utc).isoformat()
@contextmanager
def db():
    con = sqlite3.connect(DATA / 'vajrastra.db', timeout=15)
    con.row_factory = sqlite3.Row
    try:
        with con: yield con
    finally:
        con.close()
def init():
    DATA.mkdir(parents=True, exist_ok=True)
    with db() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS applications(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, name TEXT, kind TEXT, mime TEXT, content BLOB, created TEXT);
        CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT);''')
def service(sid): return next((s for s in CATALOG if s['id']==sid), None)
def application(aid):
    with db() as c: row = c.execute('SELECT payload FROM applications WHERE id=?',(aid,)).fetchone()
    if not row: raise ValueError('Application not found')
    return json.loads(row[0])
def save(a):
    with db() as c: c.execute('INSERT OR REPLACE INTO applications VALUES (?,?)',(a['id'],json.dumps(a)))
    return a
def checked_fields(p):
    fields = {k:str(p.get(k,'')).strip() for k in ['name','phone','district','address','details']}
    if any(len(v)>4000 for v in fields.values()): raise ValueError('A field is too long')
    return fields
def validate(a):
    f=a['fields']
    if len(f['name'])<2 or not re.fullmatch(r'[6-9][0-9]{9}',f['phone']): raise ValueError('Enter a name and a valid 10-digit Indian mobile number')
    if not f['district'] or not f['address']: raise ValueError('District and address are required')
    if a['service']=='grievance' and len(f['details'])<20: raise ValueError('Describe the grievance in at least 20 characters')
    with db() as c:
        kinds=[r[0] for did in a['documents'] for r in c.execute('SELECT kind FROM documents WHERE id=?',(did,))]
    missing=set(service(a['service'])['documents'])-set(kinds)
    if missing: raise ValueError('Add required documents: '+', '.join(sorted(missing)))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def send(self,status,data,mime='application/json',extra=None):
        raw=json.dumps(data,ensure_ascii=False).encode() if mime=='application/json' else data
        self.send_response(status)
        for k,v in {'Content-Type':mime,'Content-Length':str(len(raw)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",**(extra or {})}.items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(raw)
    def valid_host(self):
        return self.headers.get('Host') in [f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}']
    def do_GET(self):
        if not self.valid_host(): return self.send(403,{'error':'Local host only'})
        path=urlparse(self.path).path
        if path=='/api/bootstrap':
            with db() as c:
                apps=[json.loads(r[0]) for r in c.execute('SELECT payload FROM applications ORDER BY rowid DESC')]
                docs=[dict(r) for r in c.execute('SELECT id,name,kind,mime,created FROM documents ORDER BY rowid DESC')]
                prefs=c.execute('SELECT payload FROM settings WHERE id=1').fetchone()
            return self.send(200,{'services':CATALOG,'applications':apps,'documents':docs,'settings':json.loads(prefs[0]) if prefs else {},'mode':'demo','ocr':bool(shutil.which('tesseract')),'assistant':'gateway' if os.environ.get('ASSISTANT_GATEWAY_URL') else 'local'})
        if path.startswith('/api/documents/'):
            with db() as c: r=c.execute('SELECT mime,content FROM documents WHERE id=?',(path.split('/')[-1],)).fetchone()
            return self.send(200,r[1],r[0],{'Content-Disposition':'attachment; filename="document"'}) if r else self.send(404,{'error':'Not found'})
        allowed={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css','/favicon.svg':'favicon.svg'}
        if path not in allowed: return self.send(404,{'error':'Not found'})
        f=ROOT/'public'/allowed[path]
        mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml'}[f.suffix]
        self.send(200,f.read_bytes(),mime)
    def do_POST(self):
        if not self.valid_host(): return self.send(403,{'error':'Local host only'})
        origin=self.headers.get('Origin')
        if origin and origin not in [f'http://localhost:{self.server.server_port}',f'http://127.0.0.1:{self.server.server_port}']: return self.send(403,{'error':'Origin rejected'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.send(415,{'error':'JSON required'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<12*1024*1024: return self.send(413,{'error':'Request is too large'})
            p=json.loads(self.rfile.read(length))
            if not isinstance(p,dict): raise ValueError('Expected an object')
            with LOCK: result=self.action(urlparse(self.path).path,p)
            self.send(200,result)
        except (ValueError,KeyError,TypeError,binascii.Error) as e: self.send(400,{'error':str(e)})
        except Exception: self.send(500,{'error':'The request could not be completed. Please retry.'})
    def action(self,path,p):
        if path=='/api/settings':
            settings={k:p[k] for k in ['language','largeText','contrast','spoken'] if k in p}
            with db() as c: c.execute('INSERT OR REPLACE INTO settings VALUES (1,?)',(json.dumps(settings),))
            return settings
        if path=='/api/documents':
            raw=base64.b64decode(p['content'],validate=True)
            mime=p['mime']
            if len(raw)>8*1024*1024 or not raw: raise ValueError('Use a file between 1 byte and 8 MB')
            signatures={'image/png':raw.startswith(b'\x89PNG\r\n\x1a\n'),'image/jpeg':raw.startswith(b'\xff\xd8\xff'),'application/pdf':raw.startswith(b'%PDF-')}
            if not signatures.get(mime): raise ValueError('Upload a valid PNG, JPG, or PDF')
            kinds={k for s in CATALOG for k in s['documents']}|{'Supporting evidence'}
            if p['kind'] not in kinds: raise ValueError('Unknown document type')
            did=secrets.token_hex(12); name=Path(str(p['name'])).name[:150]
            with db() as c: c.execute('INSERT INTO documents VALUES (?,?,?,?,?,?)',(did,name,p['kind'],mime,raw,now()))
            return {'id':did,'name':name,'kind':p['kind'],'mime':mime}
        if path=='/api/documents/delete':
            with db() as c:
                used=any(p['id'] in json.loads(r[0])['documents'] for r in c.execute('SELECT payload FROM applications'))
                if used: raise ValueError('This document is attached to an application. Remove the draft first, or retain its submitted record.')
                c.execute('DELETE FROM documents WHERE id=?',(p['id'],))
            return {'ok':True}
        if path=='/api/ocr':
            if not shutil.which('tesseract'): raise ValueError('Local OCR is not installed. Enter the details manually, or install Tesseract as described in the README.')
            with db() as c: r=c.execute('SELECT mime,content FROM documents WHERE id=?',(p['id'],)).fetchone()
            if not r or r[0]=='application/pdf': raise ValueError('Select a JPG or PNG for text extraction')
            with tempfile.TemporaryDirectory() as temp:
                source=Path(temp)/('document.png' if r[0]=='image/png' else 'document.jpg'); source.write_bytes(r[1])
                result=subprocess.run(['tesseract',str(source),'stdout','-l',os.environ.get('OCR_LANGUAGES','eng')],capture_output=True,text=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if result.returncode: raise ValueError('OCR could not read this image. Try a clearer photo or enter the details manually.')
            return {'text':result.stdout[:12000]}
        if path=='/api/applications':
            s=service(p['service'])
            if not s: raise ValueError('Unknown service')
            a=application(p['id']) if p.get('id') else {'id':'VAJ-'+secrets.token_hex(4).upper(),'service':s['id'],'status':'Draft','created':now(),'events':[]}
            if a['status'] not in ['Draft','Needs correction']: raise ValueError('This application cannot be edited')
            if a['service']!=s['id']: raise ValueError('Service cannot change')
            if not isinstance(p.get('documents',[]),list): raise ValueError('Documents must be a list')
            a.update(fields=checked_fields(p.get('fields',{})),documents=list(dict.fromkeys(p.get('documents',[]))),updated=now())
            return save(a)
        if path=='/api/applications/delete':
            a=application(p['id'])
            if a['status']!='Draft': raise ValueError('Only drafts can be deleted')
            with db() as c: c.execute('DELETE FROM applications WHERE id=?',(a['id'],))
            return {'ok':True}
        if path=='/api/applications/submit':
            a=application(p['id'])
            if a['status'] not in ['Draft','Needs correction']: raise ValueError('Already submitted')
            if p.get('consent') is not True: raise ValueError('Please verify the application and give consent')
            validate(a)
            a.update(status='In review',updated=now(),consentAt=now())
            a['events'].append({'time':now(),'status':'In review','message':'Saved to the local demonstration queue. No government submission or payment was made.'})
            return save(a)
        if path=='/api/applications/simulate':
            a=application(p['id'])
            if a['status']!='In review': raise ValueError('Only applications in review can receive a demo decision')
            status=p.get('status')
            if status not in ['Completed','Needs correction']: raise ValueError('Unknown decision')
            reason=str(p.get('reason','')).strip()[:1000]
            if status=='Needs correction' and not reason: raise ValueError('A correction reason is required')
            a.update(status=status,updated=now())
            a['events'].append({'time':now(),'status':status,'message':reason or 'Demonstration completed. This is not an issued government document.'})
            return save(a)
        if path=='/api/chat':
            msg=str(p.get('message','')).strip()[:2000]; lang=p.get('language','en')
            if not msg: raise ValueError('Enter a message')
            gateway=os.environ.get('ASSISTANT_GATEWAY_URL')
            if gateway:
                if not gateway.startswith('https://'): raise ValueError('Assistant gateway must use HTTPS')
                req=urllib.request.Request(gateway,data=json.dumps({'message':msg,'language':lang}).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ.get('ASSISTANT_GATEWAY_TOKEN','')})
                with urllib.request.urlopen(req,timeout=25) as r: answer=json.loads(r.read(100000))
                return {'reply':str(answer['reply'])[:6000],'services':[x for x in answer.get('services',[]) if service(x)],'source':'Connected assistant'}
            matches=[s for s in CATALOG if any(k in msg.lower() for k in s['keywords'])]
            replies={'en':'I can help you prepare an application, organize documents, or track a saved request. Choose a service below. This local guide uses keyword matching.','hi':'मैं आवेदन तैयार करने, दस्तावेज़ जोड़ने और सहेजे गए आवेदन देखने में मदद कर सकता हूँ। नीचे सेवा चुनें। यह स्थानीय गाइड कीवर्ड से काम करता है।','te':'దరఖాస్తు సిద్ధం చేయడానికి, పత్రాలు జోడించడానికి, సేవ్ చేసిన దరఖాస్తు చూడటానికి సహాయం చేస్తాను. కింద సేవను ఎంచుకోండి. ఈ స్థానిక గైడ్ కీలక పదాలను ఉపయోగిస్తుంది.'}
            if matches:
                s=matches[0]
                replies={'en':f"I can help with {s['name'].lower()}. Start the guided application below. You can save a draft and review every detail before sending it to the demo queue.",'hi':f"{s['hi']} के लिए नीचे आवेदन शुरू करें। आप ड्राफ्ट सहेज सकते हैं और डेमो कतार में भेजने से पहले विवरण जाँच सकते हैं।",'te':f"{s['te']} కోసం కింద దరఖాస్తు ప్రారంభించండి. డ్రాఫ్ట్ సేవ్ చేసి, డెమో క్యూకు పంపే ముందు వివరాలను సమీక్షించవచ్చు."}
            return {'reply':replies.get(lang,replies['en']),'services':[s['id'] for s in matches] or ['income','pension','grievance'],'source':'Local guide'}
        raise ValueError('Unknown endpoint')

if __name__=='__main__':
    init()
    server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    print(f'VAJRASTRA is ready at http://127.0.0.1:{PORT} — local demo mode',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
