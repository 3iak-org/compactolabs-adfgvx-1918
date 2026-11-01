#!/bin/bash
# Calibration against creilly11235/adfgvx-1918 (HEAD e60da03): p.153 parts 5+6 under a new 18-column
# key, and p.176 GGDAA under Lasry's nov10 key with a 20-symbol gap. Usage: calib_creilly.sh FAKE MODEL
F=$1; M=$2; cd "$(dirname "$0")"
a=$(grep "^p153_VF" msgs.txt|cut -d' ' -f2)
b='AXVAA???????????????DDAFFVAXAGGADAFDXAXXXVDGDXVXFFGXFAVVAADAGXXXAXDDGVAVAXVAXAAVVXVAVGXAXXFGXXFAAAFXVADFDXVF'
c=$(grep "^p176_GG" msgs.txt|cut -d' ' -f2)
P18=16,7,13,4,15,8,17,3,1,12,14,2,5,9,10,18,11,6
P10=9,12,7,11,3,8,16,6,14,2,10,15,5,13,1,4; S10='4ARUT1OIFSKN3-BZPVLD-JMXCWHQ2E-G0-Y-'
{
echo "icof $a $P18"; echo "icof $a,$b $P18"
for s in 1 2; do echo "jfree p153ab:real:s$s $a,$b 18 1000000 8 $s 0"; echo "jfree p153a:real:s$s $a 18 1000000 8 $s 0"; done
echo "fsq p153a:claimedperm:real $a $P18 1000000 8 1 0"
for s in $(seq 11 26); do
  echo "jfree p153ab:shuf:s$s $a,$b 18 1000000 8 $s 1"; echo "jfree p153a:shuf:s$s $a 18 1000000 8 $s 1"
  echo "fsq p153a:claimedperm:shuf:s$s $a $P18 1000000 8 $s 1"
  echo "ic p153a:shuf:s$s $a 18 20 200000 $s 1"; echo "ic p153ab:shuf:s$s $a,$b 18 20 200000 $s 1"
done
echo "ic p153a:real $a 18 20 200000 1 0"; echo "ic p153ab:real $a,$b 18 20 200000 1 0"
echo "gap p176:nov10:real:claimpos $c $P10 $S10 20 1 0 160"
echo "gap p176:nov10:real:anypos $c $P10 $S10 20 1 0 -1"
for s in $(seq 31 46); do echo "gap p176:nov10:shuf:s$s $c $P10 $S10 20 $s 1 -1"; done
~/dev/projects/ciphers/.venv/bin/python - <<'PY'
import json
k=json.load(open('keys_bourdeau.json'))
c=[l.split()[1] for l in open('msgs.txt') if l.startswith('p176_GG')][0]
for i,e in enumerate(k):
    if i==6: continue
    print("gap p176:key%d:real:anypos %s %s %s 20 1 0 -1"%(i,c,','.join(map(str,e['perm'])),e['square']))
PY
} | xargs -P 8 -L 1 $F $M
# Second pass (results/C_creilly_fixedperm.txt): the claimed transposition held fixed, square free, both parts jointly.
# for s in 1..8 (real) and 11..26 (shuffled): jfree p153ab:claimedperm:{real,shuf}:sS A,B 18 2000000 8 S {0,1} P18
