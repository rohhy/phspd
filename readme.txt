
ERA model db:
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


1)  disable browser proxy

2) deneid
python phsptools.py --adduser none
python phsptools.py --addhttps "denied" "scripts\denied.py" 2
python phsptools.py --grant none denied 2
https://localhost/denied -> denied.py

3) cmd - nok
python phsptools.py --addhttps "/cmd" "sctripts\cmd.py" 2
python phsptools.py --adduser client
python phsptools.py --grant client cmd 2
https://localhost/cmd -> wrong redirection


4) shell
python phsptools.py --adduser client
python phsptools.py --addhttps "/shell" "scripts\cmd.py" 2
python phsptools.py --grant client "/shell" 2
https://localhost/shell -> cmd.py

