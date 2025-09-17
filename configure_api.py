#!/usr/bin/env python3
"""
DeepSeek API 配置助手
帮助用户配置DeepSeek API密钥
"""

import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("🤖 DeepSeek API 配置助手")
    print("=" * 60)
    print()

    # 检查配置文件
    config_file = Path(__file__).parent / "deepseekkey.txt"

    print("📋 当前配置状态:")
    if config_file.exists():
        print("✅ 配置文件存在")

        # 读取当前配置
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'your-deepseek-api-key-here' in content:
                print("⚠️  API密钥未配置（使用默认占位符）")
                needs_config = True
            else:
                print("✅ API密钥已配置")

                # 检查密钥格式
                for line in content.split('\n'):
                    if line.strip().startswith('api_token:'):
                        api_key = line.split(':', 1)[1].strip()
                        if api_key.startswith('sk-') and len(api_key) > 20:
                            print("✅ API密钥格式正确")
                            needs_config = False
                        else:
                            print("⚠️  API密钥格式可能有问题")
                            needs_config = True
                        break
                else:
                    needs_config = True
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            needs_config = True
    else:
        print("❌ 配置文件不存在")
        needs_config = True

    print()

    if needs_config:
        print("🔧 需要配置DeepSeek API密钥")
        print()
        print("📝 获取API密钥步骤:")
        print("1. 访问 https://platform.deepseek.com")
        print("2. 注册/登录账户")
        print("3. 进入API密钥管理页面")
        print("4. 创建新的API密钥")
        print("5. 复制密钥（格式：sk-xxxxxxxxxx）")
        print()

        api_key = input("请输入你的DeepSeek API密钥: ").strip()

        if not api_key:
            print("❌ 未输入API密钥，退出配置")
            return

        if not api_key.startswith('sk-'):
            print("⚠️  警告：API密钥通常以 'sk-' 开头")
            continue_anyway = input("是否继续配置？(y/N): ").strip().lower()
            if continue_anyway not in ['y', 'yes']:
                print("❌ 用户取消配置")
                return

        # 更新配置文件
        try:
            config_content = f"""# DeepSeek API 配置文件
# 请在下方配置你的DeepSeek API密钥

# API基础URL（通常不需要修改）
base_url: https://api.deepseek.com

# 你的DeepSeek API密钥
api_token: {api_key}

# API请求超时时间（秒）
timeout: 60

# 最大重试次数
max_retries: 3

# 配置说明：
# 1. API密钥已配置完成
# 2. 如需修改，请直接编辑此文件或重新运行配置脚本
# 3. 配置完成后重启服务器即可生效
"""

            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            print("✅ API密钥配置成功!")
            print(f"📁 配置文件位置: {config_file}")

        except Exception as e:
            print(f"❌ 配置失败: {e}")
            return

    print()
    print("=" * 60)
    print("🎉 配置完成!")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("1. 重启服务器: python start_all.py")
    print("2. 访问Web界面: http://localhost:8081")
    print("3. 点击 '测试 DeepSeek API' 验证配置")
    print()
    print("💡 提示:")
    print("- 如果测试失败，请检查API密钥是否正确")
    print("- 如果网络连接有问题，请检查防火墙设置")
    print("- API密钥需要有充足的使用额度")

if __name__ == "__main__":
    main()