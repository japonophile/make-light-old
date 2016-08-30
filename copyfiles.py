import os

with open('po/PYPOTFILES') as pypotfiles:
    for f in pypotfiles.readlines():
        ff = f[3:]
        ff = ff[:-1]
        os.system("cp %s /usr/lib/python2.7/dist-packages/%s" % (ff, ff))
for ff in ['make_light/logic/challenges.py', 'make_light/paths.py', 'make_light/utils.py']:
    os.system("cp %s /usr/lib/python2.7/dist-packages/%s" % (ff, ff))
os.system("cp -Rf challenge_groups/locales /usr/share/make-light/challenge_groups/")
os.system("cp locale/ja/LC_MESSAGES/make-light.mo /usr/share/locale/ja/LC_MESSAGES/")
os.system("cp bin/make-light /usr/bin/make-light")

