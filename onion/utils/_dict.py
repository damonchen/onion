#coding=utf-8


class JsDict(dict):

    def __getattr__(self, key):
        try:
            v = self[key]
        except:
            v = None
        return v

    def __setattr__(self, key, value):
        self[key] = value


if __name__ == '__main__':
    k = JsDict()

    k.a = 'b'
    print k
