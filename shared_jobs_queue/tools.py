# From bs_utils at https://github.com/brunorafael223
import pickle


class fpkl:
    "Read/Write pickle files"

    @staticmethod
    def read(path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        return data

    @staticmethod
    def write(path, data, protocol=4):
        with open(path, "wb") as f:
            pickle.dump(data, f, protocol=protocol)


# Text Files
################################################################################
class ftext:
    @staticmethod
    def read(path, **kwargs):
        with open(path, "r") as f:
            data = f.read(**kwargs)
        return data

    @staticmethod
    def write(path, data, **kwargs):
        with open(path, "w") as f:
            f.writelines(data, **kwargs)

    @staticmethod
    def append(path, data, **kwargs):
        with open(path, "a+") as f:
            f.writelines(data, **kwargs)


# ENDFILE
