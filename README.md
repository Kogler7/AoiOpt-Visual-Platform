# 网格世界可视化平台 GridWorld-Visual-Platform

A Platform for GridWorld Visualization



## 1 使用说明

### 1.1 基本概念

- 坐标系统
  
  > 在`GridWorld`中，逻辑坐标（crd）和物理坐标（pos）均以`QPoint`类（整型二维点）表示，地理坐标（geo）以`QPointF`（浮点型二维点）表示，由`LayoutDeputy`负责维护相关数据，并提供逻辑坐标、物理坐标以及地理坐标互相转换的函数。
  
  - 设备坐标系统
    - 沿用Qt默认坐标系统，以**设备左上角**为原点，**从右至左**为X轴正方向，**从上至下**为Y轴正方向。
  - 物理坐标、逻辑坐标
    - 物理坐标系即窗口设备坐标系，以**窗口左上角**为原点，**单位为像素**，X坐标向右增长，Y坐标向下增长。
    - 逻辑坐标系是`GridWorld`采用的基础坐标系，单位为**格**，以每格**左上角所在点**代表整个格子的坐标。
  - 地理坐标及其精度
  - 考虑到未来可能需要对**实际地图**进行可视化比对，`GridWorld`提供了对**经纬度坐标**的简单支持。
    - 默认逻辑坐标原点对应实际地理坐标（39.910°N，116.400°E，**北京天安门**）。
    - 默认**地理坐标精度**（即每单位逻辑坐标对应经纬度大小）为**0.001**（约111米）。
  
- 布局系统

  > 为提升性能，GridWorld2.0之后在渲染AOI以及轨迹包裹时利用了Qt的映射机制。

  - 物理视窗`Viewport`（视口）
    - 物理视窗（也称为视口）默认等于Qt绘图设备（device）的**物理尺寸**，即**以像素为单位**的画布大小。
    - `QPainter`提供了`setViewport`方法，可以动态调整绘图设备的视口大小。当视口小于设备尺寸时，超过视口的部分不会被绘制，即使其没有超出设备尺寸；而当视口大于设备尺寸时，超出设备尺寸的部分也不会被绘制。
    - 在Qt的映射机制中，视口最重要的作用就是作为窗口（即逻辑视窗）的**参照**。
  - 逻辑视窗`Window`（窗口）
    - 相对于视口是以真实像素为单位的画布大小，窗口其实是一个**逻辑概念**。Qt中，视口反映了设备的真实物理尺寸，而窗口则指定了逻辑坐标和真实物理像素坐标之间的**映射关系**。
    - 例如，设置一个物理设备的视口大小为1000x1000，而窗口大小设置为100x100，则逻辑坐标（100，100）对应设备像素坐标（1000，1000），其余以此类推。
  - 映射机制
    - Qt底层实现了高效的窗口—视口映射算法，因而在完成**缩放**、**平移**等任务时，利用该机制可以大幅提升性能。

- 渲染系统

  > 图层是渲染系统的核心。层次渲染。两步缓冲渲染方式
  
- 数据格式

  - AOI数据格式
  - 轨迹和包裹
  - 其他数据



### 1.2 代码启动

- 创建GridWorld

```python
app = QApplication([]) # Qt应用启动函数，应在启动前调用
world = GridWorld() # 创建GridWorld实例
```

- 配置GridWorld

> GridWorld配置阶段可以进行一些简单的设置。可以通过GridWorld实例来获取其中的代理对象或图层对象。

```python
world.state_deputy.read_aoi("./data/aoi/AOI_20_grid.npy")
world.aoi_layer.on_reload()

world.state_deputy.read_aoi("./data/images/2.jpg")
world.state_deputy.read_traces("./data/trace/trace_1.npy")
world.state_deputy.read_parcels("./data/parcels/parcels_n.npy")

indexes = range(10)
world.trace_layer.set_indexes(indexes)
world.parcel_layer.set_indexes(indexes)
```

- 创建异步任务
>GridWorld启动后会进入**事件循环**，以保证能时刻对用户输入做出反应。任何在主线程进行的耗时任务均会造成**线程阻塞**，进而导致可视化**窗口卡死**。因此，必须开启子线程来**同步处理**其他计算任务。GridWorld2.0对多线程提供了简单的支持。在GridWorld3.0中，`AsyncProxy`提供了更为方便、强大的支持。

在GridWorld3.0之后，创建**异步任务**的方法之一便是继承`AsyncWorker`类并实现`runner`方法，并通过`AsyncProxy`**申请线程**启动该任务，`AsyncWorker`的定义如下：

```python
class AsyncWorker(QObject):
    @abstractmethod
    def runner(self):
        pass
```

设`worker`为继承了`AsyncWorker`类的一个**实例化对象**，则启动该任务时只需：

```python
AsyncProxy.start(worker)
```

  - 添加信号和槽

> **信号和槽**是Qt中的一个重要概念。信号的本质是**广播的事件**，而槽则是订阅该事件的回调函数。**在**Qt中，信号和槽实现了**发布-订阅模式**，但二者并非是双向深度绑定的。利用信号和槽，可以实现异步任务之间的通讯和互相调度。在Qt中，信号（`Signal`）必须声明为**类变量**（而不能是实例变量），且必须在**类初始化阶段**（`__init__`）完成与槽的绑定。使用`Signal.connect`方法与槽绑定，使用`Signal.emit`方法发布消息（信号）。

以在GridWorld中申请线程运行深度学习算法为例，展示信号和槽在线程之间的通讯起到的作用。

```python
class LearnWorker(AsyncWorker):
    signal = Signal(tuple)  # 必须声明为类变量，可在括号内指定需要传输的数据类型

    def __init__(self, world: GridWorld, info: InfoLayer):
        super(LearnWorker, self).__init__()
        self.aoi_learning = PolicyGradientRL()  # 在init阶段声明的变量为实例变量，不可在此定义Signal
        self.signal.connect(self.update)  # 使用connect方法与槽绑定，当信号发出消息时，update函数会被调用
        self.world = world
        self.info = info

    def update(self, data):  # 异步任务拿到信号并随时发送消息，主线程收到后根据得到的数据更新可视化内容
        aoi_map = data[0]
        self.world.aoi_layer.on_reload(aoi_map)
        self.info.on_reload(data)

    def runner(self):  # 子线程主要执行的任务，即启动深度学习
        self.aoi_learning.execute(self.signal)  # 将signal传给异步任务
```

  - 动态申请线程

> 在GridWorld3.0之后，`AsyncProxy`本质是一个**全局线程池**，调用`start`或`run`方法即可自动完成线程的申请，并运行指定的任务。

设计并继承了上述`AsyncWorker`类之后，按如下方法即可启动：

```python
learner = LearnWorker(world, info_layer) # 类的实例化
AsyncProxy.start(learner) # 申请并启动线程
```

  - 动态送回数据

> 一般情况下，异步任务中可能需要将运算过程产生的数据传回主线程的可视化部分。推荐的做法是，在`AsyncWorker`子类中声明一个Signal，并将该signal通过`runner`函数传给子线程。在子线程运行过程中，可以随时通过该`signal`传回数据并触发主线程的绘图更新函数。

例如，在子线程的某一个过程中执行下列指令：

```python
if self.signal:  # 以防在未传入signal时报错
    data = (
        self.event,
        (j, i, int(act[0])),
        (int(reward0), int(reward1), int(reward_one)),
        (0, 0)
    )  # 根据需要定义data
    self.signal.emit(data)  # 通过signal将data传回主线程并启动槽函数
```

- 进入事件循环

> 完成初始化配置并启动异步任务之后，再调用以下两个方法。此后主线程会进入事件循环，且**不会主动退出**，因此不建议在该指令后执行其他指令。

```python
world.show() # 显示窗口
sys.exit(app.exec()) #进入事件循环（固定用法）
```



### 1.3 基本操作

- 框选

> 在窗口中`按住`**鼠标左键**并拖动即可框选部分栅格，松开鼠标左键后完成框选。框选时不会触发图层的`on_stage`方法，而只会不断触发`on_paint`方法。

- 拖动

> 在窗口中`按住`**鼠标右键**即可拖动整个画布。拖动时会不断触发图层的`on_stage`方法。

- 缩放

> 在窗口中`滚动`**鼠标滚轮**即可缩放整个画布，该缩放为**定点缩放**，即鼠标指针对应的逻辑坐标保持不变。缩放时会不断触发图层的`on_stage`方法。

- 滑动

> 在窗口中`点按`**鼠标中键**会进入滑动模式，再次点按鼠标中键则会退出滑动模式。滑动时画布会以点按时的鼠标指针坐标为原点，鼠标指针当前坐标为终点的向量作为滑动的**速度向量**进行定向平移。此过程中会不断触发图层的`on_stage`方法。

- 归位

> 在窗口中`双击`**鼠标中键**，画布AOI区域会自动归位至窗口中心。此过程中会不断触发图层的`on_stage`方法。



## 2 代码架构

### 2.1 网格世界代理 GridWorld Deputy

> Deputy，有副手、代理之意，其负责管理GridWorld的部分数据，代理部分操作，作为**单例对象**依附于**GridWrold**而存在，是GridWorld的专属组成部分，不可在项目的其他地方创建新实例。

#### 2.1.1 数据代理 `DataDeputy`

#### 2.1.2 状态代理 `StateDeputy`

#### 2.1.3 布局代理 `LayoutDeputy`

#### 2.1.4 渲染代理 `RenderDeputy`

#### 2.1.5 菜单代理 `MenuDeputy`

----

### 2.2 全局代理 GlobalProxy

> Proxy，指受托人、代表，在本项目中作为一种**连接层单元**而存在，可**全局访问**并**创建实例**，全局代理可以简化某些工具的使用流程，提高工作效率。

#### 2.2.1 图层代理 `LayerProxy`

> 本质是图层定义接口。

#### 2.2.2 异步代理 `AsyncProxy`

> 本质是线程池。

#### 2.2.3 数据代理 `DataProxy`

> 负责集中管理某一类数据。

#### 2.2.4 提示代理 `TooltipProxy`

> 负责集中管理提示集合。



----

### 2.3 辅助工具 Utils

#### 2.3.1 三阶曲线集合 `BezierCurves`

#### 2.3.2 色彩管理工具 `ColorSet`

#### 2.3.3 文本提示工具 `Tooltip`

#### 2.3.4 性能测算工具 `XPSChecker`

#### 2.3.5 二维处理函数库 `Custom2D`



----

### 2.4 图层定义 Layers

> 在`GridWorld`3.0 中，图层（`Layers`）是渲染系统的**核心**。`LayerProxy`定义了**图层实现接口**，所有图层均继承自该类。各图层对象负责维护自己绘图所需要的**数据**，定义自己绘图的**具体步骤**，决定自己的**绘图时机**（`on_stage`/`on_paint`）、**覆盖层次**（`level`）和**可见性**（`Visible`）等图层属性。所有自定义图层在**实例化时**会自动与`GridWorld`进行**绑定**，并将自己添加到`RenderDeputy`的**图层列表**之中，由`RenderDeputy`自动完成图层的调度和渲染。

#### 2.4.1 内置图层 Built-in Layers

> GridWorld内置了一些可以满足基本需求的图层，这些图层在`GridWorld`初始化时即被实例化，可通过`GridWorld`直接访问或操作这些图层。

- 缓冲阶段（`on_stage`）

  > 为提升绘图性能，`RenderDeputy`会将比较**耗时但无需实时更新**的任务绘制到**缓冲图层**之中。缓冲图层仅在`on_stage`阶段更新，可通过`RenderDeputy`调用`mark_need_restage`方法**主动标记更新**。

  - AOI图层
    - Level: -3（最底层）
    - 在`GridWorld`2.0之后，AOI图层以`QPixmap`（**位图**）类型存储AOI信息，其中**每一个像素代表一个逻辑方格**。
    - 在绘制时，AOI图层会借助Qt的**Window-Viewport Mapping（逻辑-物理视窗映射）**机制绘制到缓冲图层上，从而得到较为理想的性能表现。
    - 与AOI绘制有关的**布局信息**（如逻辑偏移、视窗大小等）由`LayutDeputy`负责维护。
    - 可通过调用`reload`/`update`函数**主动更新**AOI图层的数据。
  - 轨迹图层
    - Level: -2
    - 轨迹图层以**有规律的点线**来表示轨迹。
    - 在`GridWorld`2.0之后，轨迹图层以`QPixmap`（**位图**）类型来缓存轨迹绘图信息（每个逻辑方格对应**15x15**个像素）。
    - 轨迹图层以**15:1**的比例的将每一个轨迹缓存到一个**独立**的`trace_map`上，并根据需求动态绘制到设备上。
    - `trace_indexes`指示了轨迹图层在绘制时所需绘制的**轨迹的索引**，并动态管理`trace_map`的集合。
    - 轨迹图层实现了**懒加载**机制以提高性能表现，不在视窗范围内的轨迹不会被绘制。
    - 相关布局信息的维护方式和数据更新方式同上。
  - 包裹图层
    - Level: -1
    - 包裹图层以略小于逻辑方格的**彩色嵌套矩形**来表示包裹。
    - 包裹图层的绘制逻辑类似于轨迹图层，不同的是在`parcels_map`上每**10x10**个像素对应逻辑坐标的一个方格。
  - 栅格图层
    - Level: 1
    - 栅格图层负责在设备（缓冲图层）上绘制相互垂直的线条以划分出网格区域。
    - 栅格类型分为两种：基础栅格和定位栅格。**基础栅格线细而密**，在`GridWorld`进行**缩放或平移**时暂停绘制以提高性能表现；**定位栅格线粗而疏**，在每次更新时均会绘制。
    - 栅格被设定了**最小间距**和**最大间距**，当因缩放而超出间距限制时，栅格图层会自动调整**栅格缩放等级**以适应限制。
    - 栅格缩放等级最小为0级（即每个基础栅格对应一个逻辑方格，再小则没有意义），最大为10级（再大会导致溢出）。
    - 栅格参数由`LayoutDeputy`负责维护，如`level`指示了栅格的缩放等级，而`grid_cov_fac`指示了基础栅格和定位栅格的**换算关系**。

- 实时绘制阶段（`on_paint`）

  > 实时绘制指在窗口**每次重绘时（`on_paint`）均会执行一次绘图步骤**。实时绘制的绘图设备不再是缓冲图层而是**窗口设备**。在进行图层的实时绘制前，`RenderDeputy`总会先将缓冲图层绘制到窗口上，这意味着缓冲图层上的内容总会被实时绘制的内容**覆盖**。

  - 刻度图层
    - Level: 2
    - 刻度图层负责计算每条**定位栅格线**所对应的逻辑坐标和地理坐标，并将其绘制在设备上。
    - 图层实例属性`enable_crd_mark`指示了是否标记逻辑坐标，类似的，`enable_geo_mark`指示了是否绘制地理坐标。
  - 聚焦图层
    - Level: 3
    - `StateDeputy`记录了鼠标的实时操作信息，并将其**经过或划定**的区域分别解读为聚焦点`focus_point`和聚焦框`focus_rect`，聚焦图层则负责将这些信息绘制在设备上。
  - 提示图层
    - Level: inf（最顶层）
    - 提示信息的绘制并不是基于图层实现的。它由`TooltipProxy`负责管理，并由`RenderDeputy`在所有图层绘制完成之后绘制在窗口上，因此可视为一个永远位于最顶层的虚拟图层。

#### 2.4.3 自定义图层  Custom Layers


#### 2.4.3 智能图层 Auto Layers

> 除了最基本的图层定义接口外，GridWorld还提供了一些能够解决常规自定义绘图需求的智能图层模板，通过继承该模板，只需要额外书写少量的代码即可实现一些特定的需求，从而加快实验的速度。
>
> 目前，这些智能模板**尚未处于稳定阶段**，不建议使用。




## 3 更新日志

- 1.0 架构初步搭建
  - 实现网格
  - 初步搭建坐标体系
    - Level坐标
- 2.0 缓存映射更新
  - 缓存机制
  - 全新的布局更新算法
    - 基于物理-逻辑映射
    - 新的坐标转换体系
      - 逻辑坐标、物理坐标、地理坐标
  - 全新绘制算法
    - 全新AOI绘制算法
      - 基于位图映射
    - 全新轨迹、包裹绘制算法
  - 懒加载算法
  - 初步异步支持
- 3.0 图层异步更新（pre）
  - 图层核心
    - 支持自定义图层
    - 智能图层
  - 异步代理
  - 中键操作
- 4.0 设想
  - 信息增强
  - 中断与历史

