import os, io, sys
from udpipe_sent_wrapper import UDPipeSentencer
from nltk_sent_wrapper import NLTKSentencer
from argparse import ArgumentParser
from sklearn.metrics import confusion_matrix


script_dir = os.path.dirname(os.path.realpath(__file__))
lib = os.path.abspath(script_dir + os.sep + "..")
sys.path.append(lib)

from exec import exec_via_temp
from conll_reader import space_join, read_conll


if __name__ == "__main__":


	p = ArgumentParser()
	p.add_argument("-c","--corpus",default="spa.rst.sctb",help="corpus to use or 'all'")
	p.add_argument("-d","--data_dir",default=os.path.normpath("../../../data"), help="Path to shared task data folder")
	opts = p.parse_args()

	specific_corpus = opts.corpus
	data_dir = opts.data_dir

	corpora = os.listdir(data_dir)
	if specific_corpus == "all":
		corpora = [c for c in corpora if os.path.isdir(os.path.join(data_dir, c)) if not "stan" in c]
	else:
		corpora = [c for c in corpora if os.path.isdir(os.path.join(data_dir, c)) and c== specific_corpus]


	all = []
	for corpus in corpora:

		gold_file = opts.data_dir + os.sep + corpus + os.sep + corpus + "_test.conll"
		topred_file = opts.data_dir + os.sep + corpus + os.sep + corpus + "_test.tok"

		if "por" in corpus:
			a=4

		udpipe = NLTKSentencer(lang=corpus[:3])
		conllu = io.open(topred_file, encoding="utf8").read()
		filtered = []
		for line in conllu.split("\n"):
			if "\t" in line:
				fields = line.split("\t")
				if "-" in fields[0]:
					continue
			filtered.append(line)
		conllu = "\n".join(filtered) + "\n"
		pred = [x[0] for x in udpipe.predict(conllu)]
		# pred = udpipe.predict(conllu)



		gold_feats, _,toks,_,_ = read_conll(gold_file, genre_pat = "^(..)", mode="sent",as_text=False)
		gold = [int(t['wid'] == 1) for t in gold_feats]
		conf_mat = confusion_matrix(gold, pred)

		sys.stderr.write("Evaluating on " + corpus + "\n")
		sys.stderr.write(str(conf_mat) + "\n")
		true_positive = conf_mat[1][1]
		false_positive = conf_mat[0][1]
		false_negative = conf_mat[1][0]
		prec = true_positive / (true_positive + false_positive)
		rec = true_positive / (true_positive + false_negative)
		f1 = 2*prec*rec/(prec+rec)

		sys.stderr.write("P: " + str(prec) + "\n")
		sys.stderr.write("R: " + str(rec) + "\n")
		sys.stderr.write("F1: " + str(f1) + "\n")
		with io.open("diff.tab",'w',encoding="utf8") as f:
			for i in range(len(gold)):
				f.write("\t".join([toks[i],str(gold[i]),str(pred[i])])+"\n")
		all.append("\t".join([corpus,str(prec),str(rec),str(f1)]))

print("\n".join(all))