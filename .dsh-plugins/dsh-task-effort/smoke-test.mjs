// 冒烟测试：验证本机 fork 的配置外置 + provider 门禁 + 分类逻辑
// 用法：node C:\Users\18431\.agents\.dsh-plugins\dsh-task-effort\smoke-test.mjs
import { strict as assert } from "node:assert";

const PKG = "file:///C:/Users/18431/.agents/.temp/dshshop/te/package";
const { classify, DEFAULTS } = await import(`${PKG}/lib/classify.js`);
const { providerApplicable } = await import(`${PKG}/lib/session.js`);

process.env.DSH_TASK_EFFORT_CONFIG =
  "C:\\Users\\18431\\.agents\\.temp\\dshshop\\te\\package\\smoke-config.json";

const { CONFIG_OVERRIDES } = await import(`${PKG}/lib/config.js`);

// 1) 配置文件被读到，providers 覆盖生效
assert.deepEqual(CONFIG_OVERRIDES.providers, ["opencode-goo"], "config file providers");
assert.equal(CONFIG_OVERRIDES.defaultEffort, "high", "config file defaultEffort");

const cfg = { ...DEFAULTS, ...CONFIG_OVERRIDES };

// 2) provider 门禁：opencode-goo 生效，deepseek-official 不生效
assert.equal(providerApplicable("opencode-goo", cfg.providers), true, "opencode-goo allowed");
assert.equal(providerApplicable("deepseek-official", cfg.providers), false, "deepseek-official blocked");
assert.equal(providerApplicable(undefined, cfg.providers), true, "unknown provider optimistic");

// 3) 分类：闲聊 → off，复杂 → max，显式标记优先
assert.equal(classify("谢谢", null, cfg).effort, "off", "chat -> off");
assert.equal(classify("帮我重构这个模块", null, cfg).effort, "max", "refactor -> max");
assert.equal(classify("[effort=low] 随便看看", null, cfg).effort, "low", "marker wins");
assert.equal(classify("写个冒泡排序", null, cfg).effort, "high", "default -> high");

console.log("smoke-test: OK（配置外置 / provider 门禁 / 分类 全部通过）");
