from redis import StrictRedis


if __name__ == '__main__':
    try:
        # sr = StrictRedis(host='localhost', port=6379, db=0)
        sr = StrictRedis()
        result = sr.keys()
        print(result)

    except Exception as e:
        print(e)


