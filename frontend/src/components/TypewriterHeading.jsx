import { useState, useEffect, useRef } from 'react';

/**
 * TypewriterHeading - 带打字机特效、微弱打字声音效和等宽字体的标题组件
 * 参考实现: .review/front_type.md
 * 
 * 特性:
 * - 逐字生成打字机效果，每字之间速度随机（0.5x ~ 1.5x）
 * - 打完自动退格，退完重新打字，循环往复
 * - 使用 Web Audio API 动态合成微弱打字声（无需外部音频文件）
 * - 使用 JetBrains Mono / Share Tech Mono 开源等宽字体
 * - 带闪烁光标动画
 */
export default function TypewriterHeading({ text, speed = 100, className = '' }) {
  const [displayedText, setDisplayedText] = useState('');
  const modeRef = useRef('typing'); // 'typing' | 'deleting'
  const indexRef = useRef(0);
  const audioCtxRef = useRef(null);
  const runningRef = useRef(true);

  // 生成随机延迟（0.5x ~ 1.5x speed）
  const getRandomDelay = () => speed * (0.5 + Math.random());

  useEffect(() => {
    runningRef.current = true;

    // 初始化 Web Audio API 上下文
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      audioCtxRef.current = new AudioContext();
    }

    // 播放微弱打字声 / 退格声
    const playTypeSound = (isDelete = false) => {
      if (!audioCtxRef.current) return;
      try {
        const ctx = audioCtxRef.current;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        // 退格时音调略低，打字时略高
        const baseFreq = isDelete ? 400 : 600;
        osc.type = 'square';
        osc.frequency.value = baseFreq + Math.random() * 800;
        gain.gain.value = 0.03; // 音量 3%
        osc.start(ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
        osc.stop(ctx.currentTime + 0.05);
      } catch (e) {
        // 浏览器自动播放策略限制时静默处理
      }
    };

    // 状态机主循环：typing → deleting → typing → ...
    const loop = () => {
      if (!runningRef.current || !text) return;

      if (modeRef.current === 'typing') {
        if (indexRef.current < text.length) {
          const nextChar = text[indexRef.current];
          setDisplayedText(prev => {
            if (!runningRef.current) return prev;
            return prev + nextChar;
          });
          if (nextChar !== ' ') {
            playTypeSound(false);
          }
          indexRef.current++;
          setTimeout(loop, getRandomDelay());
        } else {
          // 打完了，停顿 2 秒后进入退格
          modeRef.current = 'deleting';
          setTimeout(loop, 2000);
        }
      } else {
        // deleting
        if (indexRef.current > 0) {
          setDisplayedText(prev => {
            if (!runningRef.current) return prev;
            return prev.slice(0, -1);
          });
          playTypeSound(true);
          indexRef.current--;
          setTimeout(loop, getRandomDelay());
        } else {
          // 退完了，停顿 0.8 秒后重新打字
          modeRef.current = 'typing';
          setTimeout(loop, 800);
        }
      }
    };

    // 重置状态并从 0 开始
    modeRef.current = 'typing';
    indexRef.current = 0;
    setDisplayedText('');

    // 开始主循环
    const initialDelay = getRandomDelay();
    const timeoutId = setTimeout(loop, initialDelay);

    return () => {
      runningRef.current = false;
      clearTimeout(timeoutId);
    };
  }, [text, speed]);

  return (
    <h1
      className={`typewriter-cursor ${className}`}
      style={{
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace",
        fontSize: '2rem',
        fontWeight: 'bold',
        display: 'inline-block',
        paddingRight: '4px',
        whiteSpace: 'pre-wrap',
        minHeight: '2.5rem' // 保持容器高度稳定
      }}
    >
      {displayedText}
      {'\u00A0'}
    </h1>
  );
}
