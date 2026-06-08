import { useState, useEffect, useRef } from 'react';

/**
 * TypewriterHeading - 带打字机特效、微弱打字声音效和等宽字体的标题组件
 * 参考实现: .review/front_type.md
 * 
 * 特性:
 * - 逐字生成打字机效果
 * - 使用 Web Audio API 动态合成微弱打字声（无需外部音频文件）
 * - 使用 JetBrains Mono / Share Tech Mono 开源等宽字体
 * - 带闪烁光标动画
 */
export default function TypewriterHeading({ text, speed = 100, className = '' }) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const audioCtxRef = useRef(null);

  // 初始化 Web Audio API 上下文
  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      audioCtxRef.current = new AudioContext();
    }
    return () => {
      if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
        audioCtxRef.current.close();
      }
    };
  }, []);

  // 播放微弱打字声（极短促的机械键盘敲击声）
  const playTypeSound = () => {
    if (!audioCtxRef.current) return;
    try {
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      // 模拟机械键盘敲击声：方波 + 快速衰减
      osc.type = 'square';
      osc.frequency.value = 600 + Math.random() * 800; // 600-1400Hz 随机
      gain.gain.value = 0.03; // 音量 3%，非常微弱
      
      osc.start(ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
      osc.stop(ctx.currentTime + 0.05);
    } catch (e) {
      // 浏览器自动播放策略限制时静默处理
    }
  };

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeoutId = setTimeout(() => {
        const nextChar = text[currentIndex];
        setDisplayedText((prev) => prev + nextChar);
        
        // 空格通常不发声，体验更好
        if (nextChar !== ' ') {
          playTypeSound();
        }
        
        setCurrentIndex((prev) => prev + 1);
      }, speed);

      return () => clearTimeout(timeoutId);
    } else {
      setIsComplete(true);
    }
  }, [currentIndex, text, speed]);

  // text 变化时重置动画
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
    setIsComplete(false);
  }, [text]);

  return (
    <h1 
      className={`typewriter-cursor ${className}`}
      style={{
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace",
        fontSize: '2rem',
        fontWeight: 'bold',
        display: 'inline-block',
        paddingRight: '4px',
        whiteSpace: 'pre-wrap'
      }}
    >
      {displayedText}
      {!isComplete && '\u00A0'}
    </h1>
  );
}
