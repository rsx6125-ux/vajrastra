"""Integration tests use a temporary database; never touch a user's records."""
import base64
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        server.DATA=Path(cls.temp.name)
        server.init()
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.port=cls.http.server_port
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join();cls.temp.cleanup()
    def request(self,path,data=None,headers=None):
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
        try:
            with urllib.request.urlopen(req) as r: return r.status,json.loads(r.read())
        except urllib.error.HTTPError as e: return e.code,json.loads(e.read())
    def draft(self,sid='grievance',**updates):
        p={'service':sid,'fields':{'name':'Demo Citizen','phone':'9000000000','district':'Demo District','address':'Sample address, test only','details':'A sample service delay for testing the grievance workflow.'},'documents':[],**updates}
        code,a=self.request('/api/applications',p);self.assertEqual(code,200,a);return a
    def test_bootstrap_and_static_assets(self):
        code,data=self.request('/api/bootstrap');self.assertEqual(code,200);self.assertEqual(len(data['services']),8)
        for path in ['/','/app.js','/style.css','/favicon.svg']:
            with urllib.request.urlopen(f'http://127.0.0.1:{self.port}'+path) as r: self.assertEqual(r.status,200);self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy'])
    def test_complete_correction_resubmission_history(self):
        a=self.draft()
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':False})[0],400)
        code,a=self.request('/api/applications/submit',{'id':a['id'],'consent':True});self.assertEqual(code,200);self.assertEqual(a['status'],'In review')
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],400)
        self.assertEqual(self.request('/api/applications',a)[0],400)
        code,a=self.request('/api/applications/simulate',{'id':a['id'],'status':'Needs correction','reason':'Clarify the resolution requested'});self.assertEqual(code,200)
        a['fields']['details']='Updated sample description with a clear resolution request.'
        self.assertEqual(self.request('/api/applications',a)[0],200)
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],200)
        code,a=self.request('/api/applications/simulate',{'id':a['id'],'status':'Completed'});self.assertEqual(code,200);self.assertEqual(len(a['events']),4)
        self.assertEqual(self.request('/api/applications/delete',{'id':a['id']})[0],400)
    def test_missing_documents_and_document_reuse(self):
        a=self.draft('residence')
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],400)
        for kind in ['Identity proof','Address proof']:
            code,d=self.request('/api/documents',{'name':'sample.pdf','kind':kind,'mime':'application/pdf','content':base64.b64encode(b'%PDF-1.4\nSample only').decode()});self.assertEqual(code,200);a['documents'].append(d['id'])
        self.assertEqual(self.request('/api/applications',a)[0],200)
        self.assertEqual(self.request('/api/documents/delete',{'id':d['id']})[0],400)
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],200)
    def test_invalid_file_rejected(self):
        self.assertEqual(self.request('/api/documents',{'name':'fake.png','mime':'image/png','kind':'Identity proof','content':base64.b64encode(b'<script>bad</script>').decode()})[0],400)
    def test_invalid_phone_rejected(self):
        a=self.draft(fields={'name':'Demo','phone':'123','address':'Test','district':'Test','details':'Long sample grievance content'});self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],400)
    def test_origin_and_host_protection(self):
        self.assertEqual(self.request('/api/settings',{}, {'Origin':'https://untrusted.example'})[0],403)
        self.assertEqual(self.request('/api/bootstrap',headers={'Host':'untrusted.example'})[0],403)
    def test_multilingual_guide(self):
        for lang,msg,sid in [('en','I need income proof','income'),('hi','पेंशन चाहिए','pension'),('te','ఆరోగ్య పథకం','health')]:
            code,r=self.request('/api/chat',{'language':lang,'message':msg});self.assertEqual(code,200);self.assertIn(sid,r['services']);self.assertTrue(r['reply'])
    def test_persistence_and_preferences(self):
        self.request('/api/settings',{'language':'te','largeText':True,'contrast':False,'spoken':False})
        server.init()
        self.assertEqual(self.request('/api/bootstrap')[1]['settings']['language'],'te')
    def test_draft_deletion(self):
        a=self.draft();self.assertEqual(self.request('/api/applications/delete',{'id':a['id']})[0],200)
        self.assertEqual(self.request('/api/applications/submit',{'id':a['id'],'consent':True})[0],400)
    def test_unknown_service_and_route(self):
        self.assertEqual(self.request('/api/applications',{'service':'unknown'})[0],400)
        self.assertEqual(self.request('/not-a-file')[0],404)

if __name__=='__main__': unittest.main(verbosity=2)
