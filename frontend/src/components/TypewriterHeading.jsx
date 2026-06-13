import { useState, useEffect, useRef } from 'react';
import useStore from '../store';

/**
 * TypewriterHeading - 带打字机特效、微弱打字声音效和等宽字体的标题组件
 * 参考实现: .review/front_type.md
 * 
 * 特性:
 * - 逐字生成打字机效果，每字之间速度随机（0.3x ~ 1.7x），偶尔有长时间停顿
 * - 打完自动退格，退完重新打字，循环往复
 * - 使用 Web Audio API 动态合成微弱打字声（无需外部音频文件）
 * - 使用 JetBrains Mono / Share Tech Mono 开源等宽字体
 * - 带闪烁光标动画
 */
export default function TypewriterHeading({ text, speed = 100, className = '', as: Tag = 'h1', fontSize = '2rem' }) {
  const [displayedText, setDisplayedText] = useState('');
  const genRef = useRef(0);
  const timeoutRef = useRef(null);
  const audioCtxRef = useRef(null);

  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext && !audioCtxRef.current) {
      audioCtxRef.current = new AudioContext();
    }

    // generation 递增，让旧循环自然死亡
    const myGen = ++genRef.current;

    let idx = 0;
    let mode = 'typing';

    const getRandomDelay = () => {
      // 基础范围: 0.3x ~ 1.7x，平均1x，整体偏慢
      let base = speed * (0.3 + Math.random() * 1.4);
      // 退格时略快
      if (mode === 'deleting') base *= 0.8;
      // 15%概率双倍停顿（像在思考）
      if (Math.random() < 0.15) base *= 2;
      // 5%概率三倍停顿
      if (Math.random() < 0.05) base *= 3;
      // 1%概率明显卡顿
      if (Math.random() < 0.01) base *= 5;
      return base;
    };

    const playSound = (isDelete = false) => {
      // 音效默认关闭，仅当用户在导航栏开启后才发声（实时读取最新值）
      if (!useStore.getState().soundEnabled) return;
      if (!audioCtxRef.current) return;
      try {
        const ctx = audioCtxRef.current;
        if (ctx.state === 'suspended') ctx.resume();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        const baseFreq = isDelete ? 350 : 550;
        osc.type = 'square';
        osc.frequency.value = baseFreq + Math.random() * 900;
        gain.gain.value = 0.025;
        osc.start(ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
        osc.stop(ctx.currentTime + 0.05);
      } catch (e) {}
    };

    const tick = () => {
      // 不是当前 generation 就立即停止
      if (genRef.current !== myGen || !text) return;

      if (mode === 'typing') {
        if (idx < text.length) {
          const ch = text[idx];
          setDisplayedText(prev => {
            // 再次检查，防止旧循环的 setState 覆盖新循环
            if (genRef.current !== myGen) return prev;
            return prev + ch;
          });
          if (ch !== ' ') playSound(false);
          idx++;
          timeoutRef.current = setTimeout(tick, getRandomDelay());
        } else {
          // 打完了，停顿 2.5 秒后进入退格
          mode = 'deleting';
          timeoutRef.current = setTimeout(tick, 2500);
        }
      } else {
        // deleting
        if (idx > 0) {
          setDisplayedText(prev => {
            if (genRef.current !== myGen) return prev;
            return prev.slice(0, -1);
          });
          playSound(true);
          idx--;
          timeoutRef.current = setTimeout(tick, getRandomDelay());
        } else {
          // 退完了，停顿 1 秒后重新打字
          mode = 'typing';
          timeoutRef.current = setTimeout(tick, 1000);
        }
      }
    };

    // 重置显示并启动
    setDisplayedText('');
    timeoutRef.current = setTimeout(tick, getRandomDelay());

    return () => {
      // generation 递增，让所有旧 tick 自然死亡
      genRef.current++;
      // 清除已排队的 timeout，防止旧 tick 再执行一次
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [text, speed]);

  return (
    <Tag
      className={`typewriter-cursor ${className}`}
      style={{
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace",
        fontSize,
        fontWeight: 'bold',
        display: 'inline-block',
        paddingRight: '4px',
        whiteSpace: 'pre-wrap',
        minHeight: '2.5rem'
      }}
    >
      {displayedText}
      {'\u00A0'}
    </Tag>
  );
}
