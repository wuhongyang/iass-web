use mapdb;
CREATE TABLE `cm_metric` (
  `id` bigint(20) auto_increment COMMENT '����',
  `metric_name` varchar(255) NOT NULL COMMENT '���������',
  `metric_desc` varchar(255) NOT NULL COMMENT '���������',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='�û���ص�metric��';

insert into cm_metric (metric_name,metric_desc) values ('cpu_usage','cpuʹ����');
insert into cm_metric (metric_name,metric_desc) values ('bytes_in','������������');
insert into cm_metric (metric_name,metric_desc) values ('bytes_out','������������');
insert into cm_metric (metric_name,metric_desc) values ('mem_usage','�ڴ�ʹ����');
insert into cm_metric (metric_name,metric_desc) values ('load_five','ƽ������');
insert into cm_metric (metric_name,metric_desc) values ('proc_run','��Ծ����');
insert into cm_metric (metric_name,metric_desc) values ('proc_total','ȫ������');
insert into cm_metric (metric_name,metric_desc) values ('reads','���̶�');
insert into cm_metric (metric_name,metric_desc) values ('writes','����д');

CREATE TABLE `cm_alarm_project` (
  `id` bigint(20) auto_increment COMMENT '������ĿId',
  `alarm_project_name` varchar(255) NOT NULL COMMENT '������Ŀ����',
  `alarm_project_desc` varchar(255) NOT NULL COMMENT '������Ŀ����',
  `alarm_group_ids` varchar(255) NOT NULL COMMENT '������id���ϣ��Զ��Ÿ��� ',
  `update_time` datetime COMMENT '����ʱ��',
  PRIMARY KEY (`id`)
)  ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='������Ŀ��';

CREATE TABLE `cm_alarm_rule` (
  `id` bigint(20) auto_increment COMMENT '��������Id',
  
  `alarm_times` int(11) NOT NULL DEFAULT '0' COMMENT '�����������ٴκ󲻱���',
  `metric_id` bigint(20) NOT NULL COMMENT '��ض����id',
  `metric_name` varchar(255) NOT NULL COMMENT '���������',
  `metric_desc` varchar(255) NOT NULL COMMENT '���������',
  `alarm_project_id` bigint(20) NOT NULL COMMENT '������Ŀid',
  
  `alarm_project_name` varchar(255) NOT NULL COMMENT '������Ŀ����',
  
  `disabled` tinyint(2) NOT NULL DEFAULT '0' COMMENT '�Ƿ���Ч',
  `alarm_frequency` int(11) NOT NULL DEFAULT '0' COMMENT '�¼�����Ƶ�ʣ���λ�����ӣ�',
  `alarm_method` int(11) DEFAULT '1' COMMENT '�������� 1qq 2�ʼ� 3�ֻ�',
  
  `statistic` int(11) NOT NULL COMMENT '�����жϵ�ͳ��ֵ��avg 1 sum 2 max 3 min 4 ',
  `comparison_operator`  varchar(255) NOT NULL COMMENT '�����ж�������>=�ֺ�<=�ֺ�>�ֺ�<�ֺ�!=�ֺ�==',
  `threshold` double NOT NULL COMMENT '������ֵ',
  PRIMARY KEY (`id`)
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='������';

CREATE TABLE `cm_alarm_mapping` (
	 `id` bigint(20) auto_increment,
	 `alarm_project_id` bigint(20) NOT NULL COMMENT '������ĿId',
	 `fixed_ip` varchar(39) NOT NULL COMMENT 'fixed_ip is the pk of mapping table',
	 
	 `is_vm` int(1) DEFAULT '1' NULL COMMENT '�Ƿ��������',
	 
	 `alarm_group_ids` varchar(255) NOT NULL COMMENT '������id���ϣ��Զ��Ÿ��� ',
	 PRIMARY KEY (`id`)
	 
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='����������Ӧ��';

CREATE TABLE `cm_alarm_history` (
  `id` bigint(20) auto_increment COMMENT '����,������',
  `alarm_rule_id` bigint(20) NOT NULL COMMENT '��������Id',
  `metric_desc` varchar(255) NOT NULL COMMENT '����ģ��',
  `alarm_time` datetime  COMMENT '��������ʱ��',
  `alarm_content_summary` varchar(1000) NOT NULL COMMENT '��Ҫ�������ݣ��ֻ��������ݣ�',
  `alarm_content` text NOT NULL COMMENT '�������� ������ �ʼ��������ݣ�',
  `alarm_group_ids` varchar(255) NOT NULL COMMENT '������id  ����������÷ֺŷָ�',
  `alarm_group_names` varchar(255) NOT NULL COMMENT '����������,����÷ֺ�(,)�ָ�',
  `fixed_ip` varchar(255) NOT NULL COMMENT '��������',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='������ʷ��¼';

CREATE TABLE `cm_alarm_history_month_count` (
  `id` bigint(20) auto_increment COMMENT '����,������',
  `count` bigint(20) NOT NULL COMMENT '��������',
  `alarm_time` datetime  COMMENT '��������ʱ�䣬��ȷ����',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='������ʷ�¼�¼';

CREATE TABLE `cm_alarm_group` (
  `id` bigint(20) auto_increment COMMENT '������Id',
  `alarm_group_name` varchar(255) NOT NULL COMMENT '����������',
  `alarm_group_desc` varchar(512) NOT NULL COMMENT '����������',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='������';

CREATE TABLE `cm_alarm_user` (
  `id` bigint(20) auto_increment COMMENT '������',
  `alarm_user_name` varchar(255) NOT NULL COMMENT '�û���',
  `email` varchar(255) NOT NULL COMMENT '�ʼ���ַ',
  `phone` varchar(255) NOT NULL COMMENT '�ֻ�',
  `qq` varchar(255) NOT NULL COMMENT 'qq',
  `remark` varchar(255) NOT NULL COMMENT '��ע',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='�������û���Ӧ��';

create  table `cm_user_group_mapping`(
    `id` bigint(20) auto_increment COMMENT '������',
	`alarm_group_id` bigint(20) NOT NULL COMMENT '������Id',
	`alarm_user_id` bigint(20) NOT NULL COMMENT '�û�Id',
	`alarm_group_name` varchar(255)  COMMENT '����������',
	`alarm_user_name` varchar(255)  COMMENT '�û���',
	`alarm_config` int(11) DEFAULT '1' COMMENT '�������� 1qq 2�ʼ� 3�ֻ�',
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='�������û���Ӧ��';

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
  `org_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '������',
  `org_name` varchar(50) NOT NULL COMMENT '��֯��������',
  `parent_name` varchar(512) NOT NULL  COMMENT '�ϼ���֯��������',
  PRIMARY KEY (`org_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `mis_umuser` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '������',
  `org_id` bigint(20) NOT NULL  COMMENT '�ϼ���֯����ID',
  `parent_name` varchar(30) NOT NULL COMMENT '�ϼ���֯��������',
  `user_name` varchar(30) NOT NULL COMMENT '�û���',
  `logon_id` varchar(30) NOT NULL COMMENT 'misϵͳ��¼��',
  `email` varchar(50) NOT NULL COMMENT '�ʼ���ַ',
  `office_phone` varchar(255) NOT NULL COMMENT '����',
  `mobile` varchar(255) NOT NULL COMMENT '�ֻ�',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `device` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '������',
  `name` varchar(50) NOT NULL COMMENT '����',
  `model` varchar(255) NOT NULL COMMENT '�ͺ�',
  `classify` varchar(255) NOT NULL COMMENT '����-��������������',
  `detail` varchar(512) NOT NULL COMMENT '����',
  `purchase_time` varchar(255) NOT NULL COMMENT '�ɹ�ʱ��',
  `online_time` varchar(255) NOT NULL COMMENT '����ʱ��',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

 CREATE TABLE `ticket` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '������',
  `tickict_no` bigint(20) NOT NULL COMMENT '�������',
  `hostname` bigint(20) NOT NULL COMMENT '���������',
  `availability_zone` varchar(255) NOT NULL COMMENT '����������',
  `flavor_id` varchar(255) NOT NULL COMMENT '�����',
  `image_ref` varchar(512) NOT NULL COMMENT '������',
  `min_count` varchar(255) NOT NULL COMMENT '���������',
  `user_name` varchar(30) NOT NULL COMMENT '�û���',
  `org_name` varchar(30) NOT NULL COMMENT '��֯��������',
  `parent_name` varchar(30) NOT NULL COMMENT '�ϼ���֯��������',
  `verify_status` int(1) DEFAULT '0' NULL COMMENT 'ȷ��״̬',
  `commit_time` varchar(255) NOT NULL COMMENT '����ʱ��',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;


