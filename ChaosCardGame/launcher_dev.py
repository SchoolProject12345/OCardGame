from Network import server

server.core.getCARDS()

style = input("Bar style [0-2]: ")
if not style.isnumeric() or int(style) not in [0,1,2]:
    print("Invalid choice. Defaulting to 1.")
    server.core.Constants.progressbar_sytle = 1
else:
    server.core.Constants.progressbar_sytle = int(style)
del style

match server.core.cleanstr(input("Would you like to `host` or `join` a party? ")):
    case "host": server.host(
        input("Choose your username: "),
        server.core.ifelse(server.core.cleanstr(input("Would you like to localhost [yes/no]? ")) == "yes",
            "127.0.0.1",
            server.net.get_ip()
        )
    )
    case "join": server.join(
        input("Choose your username: "),
        input("Enter your host IP: ")
    )
    case _: print("Unreconized action. Terminating process.")
