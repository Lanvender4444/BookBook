import { useState, useEffect, useRef } from 'react';

/**
 * TypewriterPlaceholder - 带打字机特效的占位符文字
 * 用于 textarea/input 的 placeholder 替代，支持打字/退格循环
 */
export default function TypewriterPlaceholder({ text, speed = 120, className = '' }) {
  const [displayedText, setDisplayedText] = useState('');
  const genRef = useRef(0);
  const timeoutRef = useRef(null);

  useEffect(() => {
    const myGen = ++genRef.current;
    let idx = 0;
    let mode = 'typing';

    const getRandomDelay = () => {
      let base = speed * (0.3 + Math.random() * 1.4);
      if (mode === 'deleting') base *= 0.8;
      if (Math.random() < 0.15) base *= 2;
      if (Math.random() < 0.05) base *= 3;
      if (Math.random() < 0.01) base *= 5;
      return base;
    };

    const tick = () => {
      if (genRef.current !== myGen || !text) return;

      if (mode === 'typing') {
        if (idx < text.length) {
          const ch = text[idx];
          setDisplayedText(prev => {
            if (genRef.current !== myGen) return prev;
            return prev + ch;
          });
          idx++;
          timeoutRef.current = setTimeout(tick, getRandomDelay());
        } else {
          mode = 'deleting';
          timeoutRef.current = setTimeout(tick, 2500);
        }
      } else {
        if (idx > 0) {
          setDisplayedText(prev => {
            if (genRef.current !== myGen) return prev;
            return prev.slice(0, -1);
          });
          idx--;
          timeoutRef.current = setTimeout(tick, getRandomDelay());
        } else {
          mode = 'typing';
          timeoutRef.current = setTimeout(tick, 1000);
        }
      }
    };

    setDisplayedText('');
    timeoutRef.current = setTimeout(tick, getRandomDelay());

    return () => {
      genRef.current++;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [text, speed]);

  return (
    <span className={className}>
      {displayedText}
    </span>
  );
}
