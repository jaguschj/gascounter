rrdtool graph mag.gif -s 'now - 240 min' -e 'now'   DEF:bx=mag.rrd:bx:AVERAGE   DEF:by=mag.rrd:by:AVERAGE   DEF:bz=mag.rrd:bz:AVERAGE   CDEF:b=bx,bx,*,by,by,*,+,bz,bz,*,+,SQRT   LINE2:bx#FF0000:Bx   LINE2:by#00FF00:By   LINE2:bz#0000FF:Bz   LINE1:b#000000:B
rrdtool graph magday.gif -s 'now - 1 day' -e 'now'   DEF:bx=mag.rrd:bx:AVERAGE   DEF:by=mag.rrd:by:AVERAGE   DEF:bz=mag.rrd:bz:AVERAGE   CDEF:b=bx,bx,*,by,by,*,+,bz,bz,*,+,SQRT   LINE2:bx#FF0000:Bx   LINE2:by#00FF00:By   LINE2:bz#0000FF:Bz   LINE1:b#000000:B
rrdtool graph consum-ph.gif -s 'now - 10 hour' -e 'now'   DEF:consum=count.rrd:consum:AVERAGE   CDEF:conph=consum,3600,*   LINE2:conph#00FF00:m³/h
rrdtool lastupdate count.rrd