# codex-model-router

一个帮你用嘴完成 **CC Switch** 和 **Codex++** 下载、安装、配置、切换与恢复的 Codex Skill。

很多人不是不想用 CC Switch 或 Codex++，而是卡在这些问题上：

- 不知道这两个软件分别能干什么。
- 不知道应该先装哪个、后装哪个。
- 不知道国产模型怎么接到 Codex。
- 不知道 Codex++ 的模型切换和增强功能怎么开。
- 不想手动翻配置、改文件、点一堆设置。
- 怕把 Codex 官方 OpenAI / ChatGPT 登录搞乱，想随时切回官方模式。

`codex-model-router` 的目标就是：让 Codex 先问清楚你想用哪个软件，然后介绍功能、给下载入口、带你安装、检查状态，并按你的目标完成配置。

[English README](README.en.md)

## 它主要帮谁

- 想用 Codex，但还不会配置 CC Switch / Codex++ 的人。
- 想用 DeepSeek、国产模型或其他第三方模型，但不想手写 Codex 配置的人。
- 想用 Codex++ 的模型切换、会话管理、导出、时间线等增强功能的人。
- 想在官方 OpenAI 登录、CC Switch 路由、Codex++ 配置之间安全切换的人。
- 已经把本地 Codex 配置搞乱，想恢复官方模式的人。

## 它会先问你什么

当你让 Codex 使用这个 Skill 时，它应该先帮你选目标：

1. **我想用 CC Switch**
   - 适合：想把 Codex 接到 DeepSeek / 国产模型 / 第三方模型。
   - 它会引导你下载 CC Switch、创建 provider、用环境变量保存 key、把 Codex 指到本地路由。

2. **我想用 Codex++**
   - 适合：想用模型切换、Codex 管理、诊断、更新、会话删除、导出 Markdown、时间线、项目移动等增强能力。
   - 它会引导你下载 Codex++、理解 relay/profile 和 UI 增强开关，并帮你检查配置。

3. **我两个都想用**
   - 适合：既要 CC Switch 切换国产模型，又要 Codex++ 增强 Codex。
   - 它会建议先把官方 Codex 登录弄稳定，再装本 Skill，再装 CC Switch / Codex++，最后逐项配置。

4. **我想恢复官方模式**
   - 适合：配置乱了、路由不对、想回到 OpenAI Official / ChatGPT 登录。
   - 它会先备份，再帮你恢复官方/default 路由，并重新检查状态。

## CC Switch 是干什么的

CC Switch 主要用来做模型和 provider 路由。

在这个 Skill 里，它的定位是：

- 帮 Codex 接 DeepSeek / 国产模型 / 第三方模型。
- 管理不同 provider。
- 让 Codex、Claude、Gemini 等工具走本地路由。
- 做 proxy、failover、MCP、prompts、skills 等相关管理。

简单说：**你想让 Codex 更方便地切换国产模型，就优先看 CC Switch。**

## Codex++ 是干什么的

Codex++ 主要用来增强 Codex 桌面端体验，也可以帮助管理模型/relay。

在这个 Skill 里，它的定位是：

- 帮你理解和配置 Codex++ 的 relay/profile。
- 帮你切换模型或保持官方 OpenAI 模式。
- 开启 Codex 增强功能，比如会话删除、Markdown 导出、项目移动、时间线、滚动恢复等。
- 检查 Codex++ 当前是否启用、是否选错 relay、是否需要重启。

简单说：**你想让 Codex 桌面端更好用，就优先看 Codex++。**

## 这个 Skill 能做什么

- 介绍 CC Switch / Codex++ 的区别和适用场景。
- 给出官方 GitHub 下载入口。
- 引导安装顺序。
- 检查 Codex 官方登录、模型路由、CC Switch、Codex++ 状态。
- 帮你用自然语言配置 CC Switch 路由。
- 帮你用自然语言配置 Codex++ 增强功能。
- 帮你在官方模式、CC Switch 路由、Codex++ 配置之间切换。
- 修改配置前自动备份。
- 出问题时恢复官方 Codex 模式。

## 安装这个 Skill

克隆或下载本仓库：

```bash
git clone https://github.com/leiJack-lo/codex-model-router.git
```

放到本地 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R codex-model-router ~/.codex/skills/
```

重启 Codex，让它重新加载本地 Skill。

然后在 Codex 里说：

```text
Use $codex-model-router to guide my CC Switch / Codex++ setup.
```

也可以直接说中文：

```text
使用 codex-model-router，先问我想用 CC Switch 还是 Codex++，然后带我下载安装和配置。
```

## 常用命令

查看总安装向导：

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide
```

只看 CC Switch 向导：

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide --target cc-switch
```

只看 Codex++ 向导：

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide --target codex-plus-plus
```

检查当前配置：

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py doctor
```

恢复官方 Codex 模式：

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py restore-official
```

## 可以直接对 Codex 这样说

```text
使用 codex-model-router，告诉我 CC Switch 和 Codex++ 分别适合做什么。
```

```text
使用 codex-model-router，带我安装 CC Switch，并配置 Codex 使用 DeepSeek。
```

```text
使用 codex-model-router，带我安装 Codex++，并开启常用 Codex 增强功能。
```

```text
使用 codex-model-router，帮我检查当前 Codex 配置有没有被 CC Switch 或 Codex++ 改乱。
```

```text
使用 codex-model-router，帮我切回官方 OpenAI / ChatGPT 登录模式。
```

## 安全提醒

- 不要把 API key、OAuth token、cookie、`auth.json`、私有配置文件发到 issue 或截图里。
- 模型 key 建议放在环境变量里，例如 `DEEPSEEK_API_KEY`。
- 这个 Skill 会尽量只输出脱敏状态，不打印密钥。
- 修改配置前会做备份。
- 运行时备份放在 `~/.codex/runtime/codex-model-router/backups`，不要提交到 GitHub。

## 相关项目

- CC Switch: <https://github.com/farion1231/cc-switch>
- BigPizzaV3 Codex++: <https://github.com/BigPizzaV3/CodexPlusPlus>
- b-nnett Codex++ tweak system: <https://github.com/b-nnett/codex-plusplus>

这些都是独立项目。`codex-model-router` 只是帮助你在本地 Codex 里更安全、更省心地下载、安装、理解、配置和切换它们。
