"""Normalise Gutenberg German into the ADFGVX plaintext alphabet A-Z0-9.
Umlauts expanded (AE OE UE SS), sentence punctuation -> X (telegraphic stop), all else dropped.
Usage: prep_corpus.py OUT.txt IN1.txt IN2.txt ...   (Gutenberg header/footer stripped)"""
import sys, re, hashlib
out = sys.argv[1]
parts = []
for fn in sys.argv[2:]:
    t = open(fn, encoding='utf-8', errors='replace').read()
    a = t.find('*** START OF'); a = t.find('\n', a) if a >= 0 else 0
    b = t.find('*** END OF'); b = b if b >= 0 else len(t)
    t = t[a:b].upper()
    for x, y in (('Ä','AE'),('Ö','OE'),('Ü','UE'),('ß','SS'),('É','E'),('È','E')):
        t = t.replace(x, y)
    t = re.sub(r'[.!?;:]+', ' X ', t)
    t = re.sub(r'[^A-Z0-9X]', '', t)
    t = re.sub(r'X{2,}', 'X', t)
    parts.append(t)
s = ''.join(parts)
open(out, 'w').write(s)
print(len(s), hashlib.sha256(s.encode()).hexdigest())
