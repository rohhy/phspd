def serverAddress(client_address):
  # -1 = wildcard 

  address_map = [ ((10, 0, 3, -1),   "https://10.0.3.101:8080/"),     \
                  ((10, 0, 0, -1),   "https://10.0.0.1:8080/"),       \
                  ((10,60,30, -1),   "https://10.60.30.14:8080/"),    \
                  ((127, 0, 0, 1),   "https://localhost:8080/"),      \
                  ((-1, -1, -1, -1), "https://84.19.66.153:8080/") ]

  print "client ip: %s"%client_address[0]
  client_ip = client_address[0].split(".")

  for map in address_map:
    for ipPos in range(0, 3):
      ipMatch = True
      if map[0][ipPos] == int(client_ip[ipPos]):
        continue
      elif map[0][ipPos] == -1:
        break
      else:
        ipMatch = False
        break

    if ipMatch == True:
      print "client match, using server address: \"%s\""%map[1]
      return map[1]

  #no found, return default address
  return adress_map[len(adress_map) -1][1]
