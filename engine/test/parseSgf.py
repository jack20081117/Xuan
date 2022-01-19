from engine.src.go import Go
import time

#弈客300手大型棋谱
#重要的事情说三遍:
#千万不要换行!
#千万不要换行!
#千万不要换行!
yk_300="(;RU[zh]SZ[19]KM[7.5]HA[0];B[pd];W[pp];B[dd];W[dp];B[jc];W[ql];B[nq];W[pr];B[kq];W[hq];B[cq];W[dq];B[cp];W[co];B[bo];W[cn];B[bn];W[cm];B[dr];W[er];B[cr];W[fq];B[no];W[ph];B[qf];W[cf];B[ch];W[bc];B[bd];W[cd];B[ce];W[cc];B[be];W[de];B[df];W[ee];B[ef];W[dc];B[fe];W[ed];B[ff];W[fd];B[gd];W[gc];B[hc];W[hd];B[ge];W[ic];B[hb];W[gb];B[id];W[ib];B[he];W[ha];B[jb];W[hd];B[hc];W[hb];B[me];W[ld];B[le];W[kd];B[jd];W[ke];B[mc];W[kf];B[lf];W[jg];B[lh];W[ji];B[hi];W[ij];B[hj];W[kj];B[ik];W[mj];B[jk];W[jj];B[kk];W[lk];B[ll];W[ml];B[lm];W[mm];B[ln];W[mn];B[mo];W[hk];B[hl];W[gk];B[gl];W[fk];B[ho];W[jq];B[jp];W[ip];B[io];W[kp];B[jo];W[lq];B[kr];W[jr];B[lr];W[fl];B[fm];W[cj];B[di];W[dj];B[ei];W[fi];B[ek];W[gh];B[hh];W[gg];B[hg];W[el];B[ej];W[gi];B[dl];W[cl];B[dm];W[em];B[en];W[dn];B[dk];W[fn];B[eo];W[fo];B[gp];W[gm];B[gq];W[gr];B[hr];W[ir];B[hp];W[hs];B[iq];W[hr];B[fp];W[ep];B[ck];W[bk];B[bj];W[il];B[jl];W[im];B[jm];W[in];B[jn];W[hm];B[pn];W[qn];B[pm];W[pl];B[rh];W[qj];B[ol];W[mh];B[qo];W[qm];B[po];W[ro];B[qp];W[rp];B[qq];W[rq];B[qr];W[rr];B[qs];W[nr];B[mq];W[mr];B[lp];W[oq];B[ps];W[os];B[ng];W[mg];B[lg];W[nh];B[og];W[oh];B[pg];W[qh];B[rg];W[ri];B[nk];W[mk];B[oj];W[li];B[jh];W[kh];B[ih];W[kg];B[pk];W[qk];B[pj];W[nn];B[on];W[nj];B[nl];W[pi];B[bm];W[bl];B[om];W[oi];B[ok];W[nm];B[al];W[rs];B[ak];W[do];B[ci];W[pq];B[oo];W[ls];B[ks];W[js];B[ko];W[go];B[pb];W[hf];B[if];W[gf];B[gj];W[fj];B[ig];W[je];B[ie];W[md];B[nd];W[lc];B[ne];W[nc];B[oc];W[nb];B[ob];W[mb];B[ka];W[la];B[kb];W[lb];B[na];W[kc];B[ac];W[ab];B[bf];W[ad];B[ae];W[ac];B[fg];W[fh];B[eh];W[ds];B[cs];W[es];B[hn];W[gn];B[si];W[sj];B[sh];W[rk];B[qg];W[qc];B[rd];W[qb];B[qd];W[rc];B[sc];W[sb];B[qa];W[ra];B[pa];W[sd];B[se];W[sc];B[oa];W[re];B[sf];W[pc];B[od];W[ma];B[op];W[jf];B[ii];W[ia];B[hd];W[fc];B[ja];W[eb];B[mf];W[bq];B[bp];W[cg];B[bg];W[eg];B[dg];W[ip];B[or];W[iq]PB[丁嘉熠]PW[张睿霖])"
go=Go()

if __name__ == '__main__':
    example="(;GM[1] FF[4]  SZ[19]  GN[]  DT[2021-12-18]  PB[Anonymous]  PW[杰克]  BR[9段]  WR[3段]  KM[375]HA[0]RU[Chinese]AP[GNU Go:3.8]RN[3]RE[B+R]TM[600]TC[3]TT[30]AP[honinbo]RL[0] "
    result=go.parseAdditionalSgf(example)
    print(result)

    time.sleep(1)

    go.transferSgf2StringAndBoard(yk_300)
    result_300=go.checkWinner(go.board)