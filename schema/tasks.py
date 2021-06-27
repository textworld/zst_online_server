
@shared_task(bind=True, base=MyTask)
def install_mysql_by_ansible(self, schema_id):
    # xxxxxx
    # 执行ansible脚本去安装mysql
    task_id = self.request.id
    schema = MySQLInstance.objects.get(pk=schema_id)
    try:
        from os.path import dirname, abspath, join
        base_dir = dirname(dirname(abspath(__file__)))
        logger.info("Base_dir: %s", base_dir)
        task = AnsibleTaskResult(task_id=task_id, status=AnsibleTaskResult.Status.Running, result="Start to execute")
        task.save()
        success = ansible_install_api(task_id, join(base_dir, "ansible-playbook/mysql.yml"), schema)
        task = AnsibleTaskResult.objects.get(task_id=task_id)
        if success:
            task.status = AnsibleTaskResult.Status.Success
        else:
            task.status = AnsibleTaskResult.Status.Failed
        task.end_time = datetime.now()
        task.save()
    except Exception as e:
        logger.error(e)
        raise
    return "success"