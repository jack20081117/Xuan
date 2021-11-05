# Xuan
Xuan是一款开源的围棋AI，其名称来源于中国古代围棋名著 **《玄玄棋经》**。

# 技术架构
Python

# 开发流程
可能需要的软件：Pycharm，VS Code

#围棋
##围棋规则浅谈
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

