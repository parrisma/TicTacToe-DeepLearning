import numpy as np

#
# Save and Load Q Value Dictionary of form
#   Key = String
#   Value = numpy array(9,float)
#


class Persistance:

    def __init__(self):
        return

    #
    # Dump the given q values dictionary to a simple text dump.
    #
    @classmethod
    def save(cls, qv, filename):
        out_f = None
        try:
            out_f = open(filename, "w")
            for state, qvals in qv.items():
                out_f.write(state)
                out_f.write(":")
                for i in range(0, len(qvals)):
                    out_f.write('{:.16f}'.format(qvals[i]) + ":")
                out_f.write("\n")
        except Exception as exc:
            print("Failed to save Q Values : " + str(exc))
            return False
        finally:
            out_f.close()
        return True

    #
    # Load the given text dump of the q values
    #
    @classmethod
    def load(cls, filename):
        in_f = None
        qv = dict()
        try:
            s_nan = str(np.nan)
            in_f = open(filename, "r")
            with in_f as qv_dict_data:
                for line in qv_dict_data:
                    itms = line.split(":")
                    qvs = np.full(9, np.nan)
                    i = 0
                    for fpn in itms[1:10]:
                        if fpn != s_nan:
                            qvs[i] = float(fpn)
                        i += 1
                    qv[itms[0]] = qvs
        except Exception as exc:
            print("Failed to load Q Values : " + str(exc))
            return None
        finally:
            in_f.close()
        return qv
