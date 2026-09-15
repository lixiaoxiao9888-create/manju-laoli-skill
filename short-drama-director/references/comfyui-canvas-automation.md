# 闭源模型与 Canvas 工作流自动化对接引擎 (Cloud Models & Canvas Workflow Engine)

本引擎专门面向 Seedance 2.0、即梦（Jimeng）等闭源云端视频模型及 Canvas 协作画布，提供提示词解耦注入、资产图映射与批量任务调度规范，实现“AI 自动完成参数装配，导演仅在关键节点审核确认”。

---

## 一、 闭源云端模型三层对接架构

```text
[分镜动力学与解耦提示词组] 
       │
       ├──> 1. 资产图/4 View 资产板绑定 (@asset_name -> 平台参考图输入)
       ├──> 2. 提示词解耦投喂 (主体层 + 环境层 + 镜头动态层)
       └──> 3. 平台参数契约 (生成时长随模型契约: Seedance 2.0 ≤15s / 即梦 5s~10s, 运镜强度, 提示词相关性, 风格预设)
       │
       ▼
[Seedance 2.0 / 即梦 / Canvas 画布 API]
```

---

## 二、 Canvas / 云端 API 批量调度模版示例 (Python)

```python
import json
import requests

def inject_shot_payload(shot_data, api_endpoint="https://api.example.com/v1/video/generate", api_key="YOUR_API_KEY"):
    """
    将单组分镜提示词与资产参考图组装为闭源平台标准请求载荷
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": shot_data.get("model", "seedance-2.0"),
        "prompt": shot_data["positive_prompt"],
        "negative_prompt": shot_data.get("negative_prompt", "blurry, low quality, distorted anatomy, text artifacts"),
        "duration": shot_data.get("duration", 15),
        "aspect_ratio": shot_data.get("aspect_ratio") or shot_data.get("user_aspect", "9:16"),  # 画幅以用户指定为准，见 aspect-ratio-adaptation.md
        "ref_images": shot_data.get("ref_images", []),
        "camera_motion": shot_data.get("camera_motion", "dynamic_follow"),
        "motion_intensity": shot_data.get("motion_intensity", "high")
    }
    
    response = requests.post(api_endpoint, headers=headers, json=payload)
    return response.json()
```

---

## 三、 平台生成批次与资产前置预估规范

每组输出提示词与分镜时，系统将自动汇总闭源平台任务资产清单：
- **视频生成任务组数**：如标准 3 分钟剧本输出 14 组视频单元（每组 12s~15s）；
- **前置参考图需求**：角色资产 4 View 板（CHR-）+ 场景氛围参考图（SCN-）；
- **任务轮次预估**：按闭源平台标准生成批次统计，辅助团队高效规划生成批次与点数预算。
