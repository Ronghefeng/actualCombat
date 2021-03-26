# 查询事务隔离级别
select @@tx_isolation;
# 开启事务 begin 或者 start transaction
begin
	# 事务内操作
end
# 事务提交
commit
# 提交前回滚
rollback
# 获取共享锁（读锁/S锁），其他事务只可以读取数据，不可以修改）
select * from article a where id = 1 lock in share mode;huoqu
# 获取排他锁（写锁/X锁），其他事务不可以对被锁住的记录进行任何操作（读、写、获取锁。。）
SELECT * from article a where id = 1 for UPDATE
	# for update 排他锁；lock in share mode 共享锁
	# update、delete、insert 操作，InnDB会自动加排他锁
	# select 需要用户主动添加共享锁或者排他锁

# 获取锁时会根据不同情况获取行级的排他锁或者表级的排他锁
	# 指明主键，或者查询的列建有唯一索引的情况，使用行级锁
	# 未指明主键、主键不具体（id>3）、查询普通列情况下，即未使用到索引，使用表锁

# InnoDB的行锁，锁的是索引列
# 获取共享锁之前必须先获取意向共享锁（IS）；获取排他锁之前必须先获取意向排他锁（IX）
# 意向锁为InnoDB添加和释放

begin
select * from article a where id > 12 and id < 30 for UPDATE
	# 有查询到返回值，则InnoDB会加临建锁
		# 临建锁（左开右闭）
		# 这个语句会在id<12和id>30的两个结点的相邻两边结点之间生成一个临建锁
		# 该部分数据在获取锁的事务结束之前无法被其他事务操作
		# 考虑B+树底层结构，寻找索引结点的相邻结点

	# 未查询到返回值，则InnoDB会加间隙锁
		# 这个语句会在满足id<12和id>30的结点范围以内生成一个间隙锁
		# 该部分数据在获取锁的事务结束之前无法被其他事务操作
		# 考虑B+树底层结构，寻找索引结点的相邻结点



