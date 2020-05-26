from woqlclient.woqlClient import WOQLClient

if __name__ == "__main__":
    wc = WOQLClient()
    wc.connect(str(sys.argv[1]), str(sys.argv[1]))
