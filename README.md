# Xuan
Xuan是一款开源的围棋AI，其名称来源于中国古代围棋名著 **《玄玄棋经》**。

# 技术架构
Python

# 开发流程
可能需要的软件：Pycharm，VS Code

# 围棋
## 围棋规则浅谈
**在接下来的图例中，我们默认1为黑，2为白，0为空**
* 气

一个棋子的上下左右四个交叉点若为空，就称为棋子的气。

多个相邻的同色棋子可以组成一个棋串，棋串的气为所有棋子气的总数。
如果棋串的气为0，则处于无气状态，应该从棋盘上提去。

围棋不允许走棋使自己的棋串处于无气状态。
```python
#所以，下面这个棋串无法被杀死：
#       A   B   C   D   E   F
#   1   1   1   1   1   1   0
#   2   1   0   1   0   1   0
#   3   1   1   1   1   1   0
#   4   0   0   0   0   0   0
```
在上图中，即使白棋收了黑棋棋串所有的外气，白棋也不能进入B2与D2两个点，所以这个黑棋棋串是无法被杀死的。

不过有一种特例：当走一步棋使自己的棋串处于无气状态，同时也使对方的棋串处于无气状态，则对方的棋串被提去。
```python
#也就是说，下面这个棋串会被杀死：
#       A   B   C   D                   A   B   C   D
#   1   1   1   1   2               1   0   0   0   2
#   2   1   0   1   2   ========>   2   0   2   0   2
#   3   1   1   1   2   白棋下B2后：  3   0   0   0   2
#   4   2   2   2   2               4   2   2   2   2
```
在上图中，白棋下在B2时，黑白均处于无气状态，黑子被提掉。
* 打劫

围棋不允许出现一模一样的棋形。所以当一方吃一子时，另一方不能马上吃回去。
```python
#如下情况是不被允许的：
#   0   1   2   0       0   1   2   0       0   1   2   0
#   1   2   0   2  ==>  1   0   1   2  ==>  1   2   0   2
#   0   1   2   0       0   1   2   0       0   1   2   0
#        图1                  图2                 图3
```
在上图中，我们可以看到，图1与图3完全一样，这在围棋中是不被允许的。

所以，黑落子成为图2的棋形后，必须白与黑在别处各走一手，白才能落子成为图3的棋形。
这就是打劫。

* 胜负

双方都同意计算胜负时，把所有的死棋去掉，各自算目数，目数=棋子数+围成的空数

黑方须比白多6.5目以上才能获胜，否则白获胜。
## 围棋逻辑实现
* 落子
  * Xuan会先判断落子是否合法，即是否1≤x,y≤19。再判断该点是否处于打劫状态。
  * `combine(x,y)`会尝试将当前落子点与上下左右四个方向匹配，若找到同色棋子，则会合并到棋串当中。
    ```python
    #棋串数据结构：
    {
        'black':{
            1:{
                2:{
                    'num':19
                }
            }
        }
        'white':{}
        19:[{'x':1,'y':2}]
    }
    ```
  即棋串按黑白二色区分，次级键为x,y坐标，最后则是这个棋串的编号。
  19开始则为棋串数组，管理了棋盘共有哪些元素。
  * `getStringInfo(x,y)`会根据传入的坐标获取棋串。
  * `getSrcString(*args)`会对四个方向的棋串进行选举，决定基准棋串。
  * `combineCurrentString(self,x,y,src,*args)`对这些棋串进行合并操作。
    ```python
    import logging
    def combineCurrentString(self,x,y,src,*args):
        logging.info("combine current string 处理前 string:",self.string)
        subString=self.string['black'] if self.isBlack else self.string['white']
        if x not in subString:
            subString[x]={}
        subString[x][y]=src
        subString[src].append({'x':x,'y':y})
        for s in args:
            if s>0 and s!=src and not isinstance(s,bool):
                if s in subString:
                    subString[src].extend(subString[s])
                    for key in subString:
                        if key<19:
                            for subkey in subString[key]:
                                if subString[key][subkey]==s:
                                    subString[key][subkey]=src
                    logging.info("即将删除%s"%subString[s])
                    del subString[s]
    ```