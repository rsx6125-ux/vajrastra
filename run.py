"""Start the local app and open the default browser."""
import threading
import webbrowser
import server

if __name__=='__main__':
    server.init()
    http=None
    for candidate in range(server.PORT,min(server.PORT+10,65536)):
        try:
            http=server.ThreadingHTTPServer(('127.0.0.1',candidate),server.Handler)
            break
        except OSError:
            continue
    if http is None:
        print('Could not start a local server. Close an existing instance or set PORT to an unused port.')
        raise SystemExit(1)
    url=f'http://127.0.0.1:{http.server_port}'
    threading.Timer(1,lambda:webbrowser.open(url)).start()
    print(f'VAJRASTRA is running at {url}\nKeep this window open. Press Ctrl+C to stop.\nLocal demonstration only.',flush=True)
    try: http.serve_forever()
    except KeyboardInterrupt: http.server_close()
