use mapdb;
CREATE TABLE `cm_metric` (
  `id` bigint(20) auto_increment COMMENT '主键',
  `metric_name` varchar(255) NOT NULL COMMENT '监控项名称',
  `metric_desc` varchar(255) NOT NULL COMMENT '监控项描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户监控的metric表';

insert into cm_metric (metric_name,metric_desc) values ('cpu_usage','cpu使用率');
insert into cm_metric (metric_name,metric_desc) values ('bytes_in','网络流入流量');
insert into cm_metric (metric_name,metric_desc) values ('bytes_out','网络流出流量');
insert into cm_metric (metric_name,metric_desc) values ('mem_usage','内存使用率');
insert into cm_metric (metric_name,metric_desc) values ('load_five','平均负载');
insert into cm_metric (metric_name,metric_desc) values ('proc_run','活跃进程');
insert into cm_metric (metric_name,metric_desc) values ('proc_total','全部进程');
insert into cm_metric (metric_name,metric_desc) values ('reads','磁盘读');
insert into cm_metric (metric_name,metric_desc) values ('writes','磁盘写');

CREATE TABLE `cm_alarm_project` (
  `id` bigint(20) auto_increment COMMENT '报警项目Id',
  `alarm_project_name` varchar(255) NOT NULL COMMENT '报警项目名称',
  `alarm_project_desc` varchar(255) NOT NULL COMMENT '报警项目名称',
  `alarm_group_ids` varchar(255) NOT NULL COMMENT '报警组id集合，以逗号隔开 ',
  `update_time` datetime COMMENT '更新时间',
  PRIMARY KEY (`id`)
)  ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警项目表';

CREATE TABLE `cm_alarm_rule` (
  `id` bigint(20) auto_increment COMMENT '报警规则Id',
  
  `alarm_times` int(11) NOT NULL DEFAULT '0' COMMENT '连续报警多少次后不报警',
  `metric_id` bigint(20) NOT NULL COMMENT '监控对象的id',
  `metric_name` varchar(255) NOT NULL COMMENT '监控项名称',
  `metric_desc` varchar(255) NOT NULL COMMENT '监控项描述',
  `alarm_project_id` bigint(20) NOT NULL COMMENT '报警项目id',
  
  `alarm_project_name` varchar(255) NOT NULL COMMENT '报警项目名称',
  
  `disabled` tinyint(2) NOT NULL DEFAULT '0' COMMENT '是否生效',
  `alarm_frequency` int(11) NOT NULL DEFAULT '0' COMMENT '事件报警频率（单位：分钟）',
  `alarm_method` int(11) DEFAULT '1' COMMENT '报警配置 1qq 2邮件 3手机',
  
  `statistic` int(11) NOT NULL COMMENT '报警判断的统计值，avg 1 sum 2 max 3 min 4 ',
  `comparison_operator`  varchar(255) NOT NULL COMMENT '报警判断条件，>=分号<=分号>分号<分号!=分号==',
  `threshold` double NOT NULL COMMENT '报警阈值',
  PRIMARY KEY (`id`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警表';

CREATE TABLE `cm_alarm_mapping` (
	 `id` bigint(20) auto_increment,
	 `alarm_project_id` bigint(20) NOT NULL COMMENT '报警项目Id',
	 `fixed_ip` varchar(39) NOT NULL COMMENT 'fixed_ip is the pk of mapping table',
	 
	 `is_vm` int(1) DEFAULT '1' NULL COMMENT '是否是虚拟机',
	 
	 `alarm_group_ids` varchar(255) NOT NULL COMMENT '报警组id集合，以逗号隔开 ',
	 PRIMARY KEY (`id`)
	 
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警主机对应表';

CREATE TABLE `cm_alarm_history` (
  `id` bigint(20) auto_increment COMMENT '主键,无意义',
  `alarm_rule_id` bigint(20) NOT NULL COMMENT '报警规则Id',
  `metric_desc` varchar(255) NOT NULL COMMENT '报警模块',
  `alarm_time` datetime  COMMENT '报警创建时间',
  `alarm_content_summary` varchar(1000) NOT NULL COMMENT '简要报警内容（手机报警内容）',
  `alarm_content` text NOT NULL COMMENT '报警内容 （泡泡 邮件报警内容）',
  `alarm_group_ids` varchar(255) NOT NULL COMMENT '报警组id  多个报警组用分号分割',
  `alarm_group_names` varchar(255) NOT NULL COMMENT '报警组名称,多个用分号(,)分割',
  `fixed_ip` varchar(255) NOT NULL COMMENT '报警对象',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警历史记录';

CREATE TABLE `cm_alarm_history_month_count` (
  `id` bigint(20) auto_increment COMMENT '主键,无意义',
  `count` bigint(20) NOT NULL COMMENT '报警次数',
  `alarm_time` datetime  COMMENT '报警创建时间，精确到日',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警历史月记录';

CREATE TABLE `cm_alarm_group` (
  `id` bigint(20) auto_increment COMMENT '报警组Id',
  `alarm_group_name` varchar(255) NOT NULL COMMENT '报警组名称',
  `alarm_group_desc` varchar(512) NOT NULL COMMENT '报警组描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警组';

CREATE TABLE `cm_alarm_user` (
  `id` bigint(20) auto_increment COMMENT '无意义',
  `alarm_user_name` varchar(255) NOT NULL COMMENT '用户名',
  `email` varchar(255) NOT NULL COMMENT '邮件地址',
  `phone` varchar(255) NOT NULL COMMENT '手机',
  `qq` varchar(255) NOT NULL COMMENT 'qq',
  `remark` varchar(255) NOT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警组用户对应表';

create  table `cm_user_group_mapping`(
    `id` bigint(20) auto_increment COMMENT '无意义',
	`alarm_group_id` bigint(20) NOT NULL COMMENT '报警组Id',
	`alarm_user_id` bigint(20) NOT NULL COMMENT '用户Id',
	`alarm_group_name` varchar(255)  COMMENT '报警组名称',
	`alarm_user_name` varchar(255)  COMMENT '用户名',
	`alarm_config` int(11) DEFAULT '1' COMMENT '报警配置 1qq 2邮件 3手机',
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='报警组用户对应表';

 CREATE TABLE `mappings` (
  `fixed_ip` varchar(39) NOT NULL COMMENT 'fixed_ip is the pk of mapping table',
  `is_vm` int(1) DEFAULT NULL COMMENT 'distinguish vm from real machine,0 for vm and 1 for real machine,for real machine,host_* is the value of themself',
  `instance_name` varchar(255) DEFAULT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  `os_type` varchar(255) DEFAULT NULL,
  `host_address` varchar(39) DEFAULT NULL,
  `host_name` varchar(255) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `user_name` varchar(255) DEFAULT NULL,
  `project_id` varchar(64) DEFAULT NULL,
  `project_name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`fixed_ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 

CREATE TABLE `mis_umorg` (
  `org_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '无意义',
  `org_name` varchar(50) NOT NULL COMMENT '组织机构名称',
  `parent_name` varchar(512) NOT NULL  COMMENT '上级组织机构名称',
  PRIMARY KEY (`org_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `mis_umuser` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '无意义',
  `org_id` bigint(20) NOT NULL  COMMENT '上级组织机构ID',
  `parent_name` varchar(30) NOT NULL COMMENT '上级组织机构名称',
  `user_name` varchar(30) NOT NULL COMMENT '用户名',
  `logon_id` varchar(30) NOT NULL COMMENT 'mis系统登录名',
  `email` varchar(50) NOT NULL COMMENT '邮件地址',
  `office_phone` varchar(255) NOT NULL COMMENT '座机',
  `mobile` varchar(255) NOT NULL COMMENT '手机',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `device` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '无意义',
  `name` varchar(50) NOT NULL COMMENT '名称',
  `model` varchar(255) NOT NULL COMMENT '型号',
  `classify` varchar(255) NOT NULL COMMENT '种类-服务器，交换机',
  `detail` varchar(512) NOT NULL COMMENT '配置',
  `purchase_time` varchar(255) NOT NULL COMMENT '采购时间',
  `online_time` varchar(255) NOT NULL COMMENT '接入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `ticket` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '无意义',
  `tickict_no` bigint(20) NOT NULL COMMENT '工单编号',
  `hostname` bigint(20) NOT NULL COMMENT '虚拟机名称',
  `availability_zone` varchar(255) NOT NULL COMMENT '可用域名称',
  `flavor_id` varchar(255) NOT NULL COMMENT '配额编号',
  `image_ref` varchar(512) NOT NULL COMMENT '镜像编号',
  `min_count` varchar(255) NOT NULL COMMENT '虚拟机数量',
  `user_name` varchar(30) NOT NULL COMMENT '用户名',
  `org_name` varchar(30) NOT NULL COMMENT '组织机构名称',
  `parent_name` varchar(30) NOT NULL COMMENT '上级组织机构名称',
  `verify_status` int(1) DEFAULT '0' NULL COMMENT '确认状态',
  `commit_time` varchar(255) NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;


