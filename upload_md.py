import json
import os

import lark_oapi as lark
from lark_oapi.api.drive.v1 import *


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
def upload_file(client, file_path, user_access_token):
    """上传文件到飞书云文档"""
    file = open(file_path, "rb")
    file_size = os.path.getsize(file_path)
    request: UploadAllMediaRequest = UploadAllMediaRequest.builder() \
        .request_body(UploadAllMediaRequestBody.builder()
            .file_name(file_path)
            .parent_type("ccm_import_open")
            .size(str(file_size))
            .extra("{\"obj_type\": \"docx\",\"file_extension\": \"md\"}")
            .file(file)
            .build()) \
        .build()

    # 发起请求
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    response: UploadAllMediaResponse = client.drive.v1.media.upload_all(request, option)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.media.upload_all failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return None

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    
    file_token = response.data.file_token
    print(f"文件上传成功，file_token: {file_token}")
    return file_token


def create_import_task(client, file_token, mount_key, user_access_token):
    """创建导入任务"""
    request: CreateImportTaskRequest = CreateImportTaskRequest.builder() \
        .request_body(ImportTask.builder()
            .file_extension("md")
            .file_token(file_token)
            .type("docx")
            .point(ImportTaskMountPoint.builder()
                .mount_type(1)
                .mount_key(mount_key)
                .build())
            .build()) \
        .build()

    # 发起请求
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    response: CreateImportTaskResponse = client.drive.v1.import_task.create(request, option)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.import_task.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return None

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    print("导入任务创建成功")
    return response.data


def main():
    # 配置参数
    file_path = "meeting_sum.md"
    user_access_token = "u-elZfENgbpfdpYlHuTc76zagl49HBk1EPj0G01gcw2Eag"
    mount_key = "Z4ZrfFYRRlxV3Ldn1guc6xacn4c"  # 目标文件夹的key
    
    # 创建client
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 第一步：上传文件
    print("开始上传文件...")
    file_token = upload_file(client, file_path, user_access_token)
    
    if file_token is None:
        print("文件上传失败，终止流程")
        return
    
    # 第二步：创建导入任务
    print("开始创建导入任务...")
    import_result = create_import_task(client, file_token, mount_key, user_access_token)
    
    if import_result is None:
        print("导入任务创建失败")
        return
    
    print("整个流程执行完成！")


if __name__ == "__main__":
    main()