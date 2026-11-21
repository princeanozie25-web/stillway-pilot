#!/bin/bash
# pipe.sh NAME dev|sealed : full evaluation of one final run
PY=~/Developer/voxcpm-venv/bin/python
n=$1; tag=$2; flag=""; [ "$tag" = sealed ] && flag="--sealed"
export PYTHONPATH=.
case $n in
  f_unins_*) $PY tools_explore.py runs/$n --uninstructed > logs/explore_$n.log 2>&1; exit 0 ;;
esac
# dev: fast pass (no exhaustive check).  sealed: everything.
nm=""; [ "$tag" = dev ] && nm="--no-machine"
light=0
case $n in
  f_sat_*|f_flat_*|f_hidden_s?|f_iithidden_s?|f_static_s2) light=1; nm="--no-machine" ;;   # minor controls: no exhaustive check
esac
THREADS=1 $PY -m stillway.evaluate runs/$n $flag $nm > logs/eval_${tag}_$n.log 2>&1
case $n in
  f_cont_s?|f_contiit_s?) $PY tools_cont_patch.py runs/$n $flag > logs/patch_${tag}_$n.log 2>&1; exit 0 ;;
esac
case $n in
  f_iit_s1|f_vq_s1) [ "$tag" = dev ] && $PY tools_explore.py runs/$n > logs/explore_$n.log 2>&1 ;;
esac
[ "$tag" = dev ] && exit 0
[ $light = 1 ] && exit 0
$PY tools_extras.py runs/$n $flag > logs/extras_${tag}_$n.log 2>&1
case $n in
  *hidden*) $PY tools_hidden.py runs/$n $flag > logs/hidden_${tag}_$n.log 2>&1 ;;
esac
case $n in
  f_iit_s?) $PY tools_reader.py runs/$n $flag > logs/reader_${tag}_$n.log 2>&1 ;;
esac
case $n in
  f_iit_s?) $PY tools_certify_quotient.py runs/$n $flag > logs/certq_${tag}_$n.log 2>&1 ;;
esac
exit 0
