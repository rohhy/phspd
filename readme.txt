1) db ERA model:
  - path is system path
  - url-ext is: https://server-url/url-ext/...

            ACCESS
             id INT
             user-id INT
             https-id INT
             rights INT

           1             1
          ^               ^
         /                 \
        N                   N

   HTTPSs                    USERs
    id INT                    id INT
    script-path VARCHAR(128)  cert-path VARCHAR(128)
    url-ext VARCHAR(128)
    default-acess INT


2) setup
2.1) first use
disable browser (https client) proxy
initialize phsp database:
  python phsptools.py --init

2.2) deneid
python phsptools.py --adduser none
python phsptools.py --addhttps "denied" "scripts\denied.py" 2
python phsptools.py --grant none denied 2
https://localhost/denied -> denied.py

2.3) cmd - non context shell
  2.3.1) add https service script - system path and default user rights
    python phsptools.py --addhttps "/cmd" "sctripts\cmd.py" 2
  2.3.2) add https client when do not exists
    python phsptools.py --adduser client
  2.3.3) grant client access rights to service when non default rights are required
    python phsptools.py --grant client cmd 2

2.4) shell
python phsptools.py --adduser client
python phsptools.py --addhttps "/shell" "scripts\cmd.py" 2
python phsptools.py --grant client "/shell" 2
https://localhost/shell -> cmd.py

2.5) reality
python phspdb.py --addhttps "/real" "/root/scripts/real/realWeb.py" 2
  (win:) python phsptools.py --addhttps "/real" "c:\tmp\py\real\next\realWeb.py" 2
python phspdb.py --grant client "/real" 2

2.6) epg browser
python phspdb.py --addhttps "/epg" "/root/scripts/epg/epgWeb.py" 2
  (win:)   python phsptools.py --addhttps "/epg" "c:\tmp\py\epg\next\" 2
python phspdb.py --adduser client 2
python phspdb.py --grant client "/epg" 2

2.7) epg search engine
python phsptools.py --addhttps "/epgsearch" "/root/scripts/epg/epgWebSearch.py" 2
python phspdb.py --adduser client 2
python phspdb.py --grant client "/epgsearch" 2

