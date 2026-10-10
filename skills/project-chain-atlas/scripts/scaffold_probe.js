/* scaffold_probe.js —— 脚手架（assets/atlas-scaffold.html）的默认交互回归探针。
 *
 * 用法：
 *   python scripts/browser_regression.py assets/atlas-scaffold.html scripts/scaffold_probe.js
 *
 * 覆盖：导航四类入口 + 模拟器运行中切场景 + 人工确认挂起/恢复 + 取消收口 + 状态无 undefined。
 * 契约见 references/verification.md。
 */
(function () {
  function out(t) {
    var d = document.getElementById('__result');
    if (!d) { d = document.createElement('div'); d.id = '__result'; document.body.appendChild(d); }
    d.textContent += t + '\n';
  }
  window.addEventListener('error', function (e) { out('JSERROR=' + e.message); });

  var ok = 0, bad = [];
  function chk(name, cond) { if (cond) { ok++; } else { bad.push(name); } }
  function active() { var a = document.querySelector('.page.active'); return a ? a.id : null; }
  function rows() { return document.getElementById('sim-log').children.length; }
  function logTxt() { return document.getElementById('sim-log').textContent; }
  function pick(v) {
    var s = document.getElementById('sim-scenario');
    s.value = v;
    s.dispatchEvent(new Event('change'));
  }
  var statusSeen = {};

  setTimeout(function () {
    /* ---- ① 导航：四类入口 ---- */
    document.querySelector('#toc a[data-page="p-l1"]').click();
    chk('nav-sidebar', active() === 'p-l1');

    var g = document.querySelector('#p-l1 .pager button[data-goto]');
    chk('nav-pager-exists', !!g);
    if (g) { g.click(); chk('nav-pager', active() === 'p-sim'); }

    document.getElementById('btn-next').click();
    chk('nav-next', active() === 'p-l1');
    document.getElementById('btn-prev').click();
    chk('nav-prev', active() === 'p-sim');

    document.querySelector('#toc a[data-page="p-cover"]').click();
    chk('nav-cover', active() === 'p-cover');
    chk('counter-sync', document.getElementById('counter').textContent === '1 / 3');

    /* ---- ② 模拟器：运行中切场景 ---- */
    document.querySelector('#toc a[data-page="p-sim"]').click();
    pick('nohitl');
    setTimeout(function () {
      var before = rows();
      pick('short');                                  // 运行中切换
      setTimeout(function () {
        var t = logTxt();
        // 断言必须能失败：用日志里真实出现的 node 名与 message_id，不要用只存在于节点标签的文本
        chk('switch-has-new-content', t.indexOf('m-2') >= 0);
        chk('switch-no-leak', t.indexOf('work.run') < 0 && t.indexOf('out.finalize') < 0);
        out('rows: ' + before + ' -> ' + rows());

        /* ---- ③ 人工确认：挂起 → 批准 → 恢复 ---- */
        pick('happy');
        var t0 = 0;
        (function waitHitl() {
          if (!document.getElementById('sim-approve').disabled || t0 > 12000) { onHitl(); return; }
          t0 += 150;
          setTimeout(waitHitl, 150);
        })();

        function onHitl() {
          chk('hitl-status', document.getElementById('st-status').textContent === 'waiting_hitl');
          chk('hitl-approve-enabled', document.getElementById('sim-approve').disabled === false);
          document.getElementById('sim-approve').click();
          setTimeout(function () {
            chk('hitl-resolved-emitted', logTxt().indexOf('HITL_RESOLVED') >= 0);

            /* ---- ④ 取消：在下一个节点边界收口 ---- */
            pick('happy');
            setTimeout(function () {
              document.getElementById('sim-cancel').click();
              setTimeout(function () {
                var t2 = logTxt();
                chk('cancel-emitted', t2.indexOf('RUN_FINISHED') >= 0);
                chk('cancel-status', document.getElementById('st-status').textContent === 'cancelled');

                /* ---- ⑤ 状态胶囊不得出现 undefined ---- */
                var seen = Object.keys(statusSeen).join('|');
                chk('no-undefined-status', seen.indexOf('undefined') < 0);
                out('status seen: ' + seen);
                out('ok=' + ok + ' bad=' + (bad.length ? bad.join(',') : 'none'));
                out(bad.length ? 'RESULT=FAIL' : 'RESULT=PASS');
              }, 2500);
            }, 1200);
          }, 1200);
        }
      }, 2500);
    }, 1500);

    /* 状态采样 */
    setInterval(function () {
      var v = document.getElementById('st-status').textContent;
      if (v) statusSeen[v] = 1;
    }, 120);
  }, 400);
})();
