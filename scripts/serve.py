"""Local static preview with legacy extensionless URLs and audio Range requests."""
import argparse,functools,pathlib,re
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import unquote,urlsplit
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=urlsplit(path).path
        base=getattr(self.server,'base_path','')
        if base and (path==base or path.startswith(base+'/')):path=path[len(base):] or '/'
        return super().translate_path(path)
    def send_head(self):
        path=pathlib.Path(self.translate_path(self.path))
        if path.is_dir():
            # Avoid adding a slash, allowing exact legacy URLs during review.
            index=path/'index.html'
            if index.is_file():
                f=index.open('rb');self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(index.stat().st_size));self.end_headers();return f
        return super().send_head()
    def do_GET(self):
        path=pathlib.Path(self.translate_path(self.path))
        range_header=self.headers.get('Range','')
        m=re.fullmatch(r'bytes=(\d+)-(\d*)',range_header)
        if m and path.is_file():
            size=path.stat().st_size;start=int(m[1]);end=min(int(m[2]) if m[2] else size-1,size-1)
            if start>=size or end<start:self.send_error(416);return
            self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.end_headers()
            with path.open('rb') as f:
                f.seek(start);remaining=end-start+1
                while remaining:
                    b=f.read(min(65536,remaining));self.wfile.write(b);remaining-=len(b)
            return
        super().do_GET()
    def log_message(self,*args):pass
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=4173);p.add_argument('--base-path',default='');a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(Handler,directory=str(ROOT/'dist')));server.base_path=a.base_path.rstrip('/')
    print(f'Preview: http://127.0.0.1:{a.port}{a.base_path}/',flush=True);server.serve_forever()
