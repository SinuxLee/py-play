## 一些分布式理论和算法

### 分布式理论

- CAP 定理
    - 一致性（Consistency）
    - 可用性（Availability）
    - 分区容错性（Partition tolerance）
- BASE 分布式系统宽松事务
    - 基本可用（Basically Available）
    - 软状态（Soft state）
    - 最终一致性（Eventual consistency）
- ACID 数据库事务
    - 原子性（Atomicity）
    - 一致性（Consistency）
    - 隔离性（Isolation）
    - 持久性（Durability
- 一致性模型（Consistency Models）
    - 强一致性（Strong consistency）
    - 弱一致性（Weak consistency）
    - 最终一致性（Eventual consistency）
    - 顺序一致性（Sequential consistency）
    - 因果一致性（Causal consistency
- 分布式事务模型
    - 两阶段提交（2PC）
    - 三阶段提交（3PC）
    - Saga 模式（长事务管理）
    - 分布式锁

### 共识算法

- RAFT https://raft.github.io/
- Paxos（经典 Paxos、Multi-Paxos）
- Zab（Zookeeper 的协议）
- Viewstamped Replication（VR）
- Practical Byzantine Fault Tolerance（PBFT，拜占庭容错）


### 传播协议

- Gossip
