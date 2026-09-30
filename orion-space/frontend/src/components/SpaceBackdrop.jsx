import React, { useEffect, useRef } from 'react';

export default function SpaceBackdrop() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext('2d', { alpha: true });
    if (!canvas || !context) return undefined;

    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const pointer = { x: -1000, y: -1000, active: false };
    let frame = 0;
    let width = 0;
    let height = 0;
    let stars = [];
    let comet = null;
    let nextCometAt = 0;

    const resize = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const count = Math.min(142, Math.max(62, Math.round(width * height / 9000)));
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.1 + 0.25,
        alpha: Math.random() * 0.44 + 0.12,
        phase: Math.random() * Math.PI * 2,
        drift: Math.random() * 0.24 + 0.04,
      }));
      nextCometAt = performance.now() + 5000 + Math.random() * 6000;
      if (motionPreference.matches) draw(0);
    };

    const draw = (time) => {
      context.clearRect(0, 0, width, height);
      if (!motionPreference.matches && time >= nextCometAt) {
        comet = {
          start: time,
          x: width * (0.12 + Math.random() * 0.78),
          y: height * (0.08 + Math.random() * 0.52),
          length: 72 + Math.random() * 68,
          duration: 950 + Math.random() * 500,
        };
        nextCometAt = time + 8500 + Math.random() * 8500;
      }
      const cursorRadius = 148;
      stars.forEach((star) => {
        const dx = pointer.x - star.x;
        const dy = pointer.y - star.y;
        const distance = Math.hypot(dx, dy);
        const influence = pointer.active ? Math.max(0, 1 - distance / cursorRadius) : 0;
        const driftX = Math.sin(time * 0.00012 + star.phase) * star.drift;
        const driftY = Math.cos(time * 0.0001 + star.phase) * star.drift;
        const x = star.x - dx * influence * 0.055 + driftX;
        const y = star.y - dy * influence * 0.055 + driftY;
        const twinkle = motionPreference.matches ? 0 : Math.sin(time * 0.0012 + star.phase) * 0.14;
        const opacity = Math.max(0.08, Math.min(0.75, star.alpha + twinkle + influence * 0.22));

        if (influence > 0.08) {
          context.beginPath();
          context.moveTo(pointer.x, pointer.y);
          context.lineTo(x, y);
          context.strokeStyle = `rgba(211, 221, 232, ${influence * 0.075})`;
          context.lineWidth = 0.65;
          context.stroke();
        }

        context.beginPath();
        context.arc(x, y, star.radius + influence * 0.55, 0, Math.PI * 2);
        context.fillStyle = `rgba(238, 241, 245, ${opacity})`;
        context.fill();
      });

      if (comet && !motionPreference.matches) {
        const progress = Math.min(1, (time - comet.start) / comet.duration);
        const eased = 1 - (1 - progress) ** 3;
        const headX = comet.x + eased * comet.length * 1.8;
        const headY = comet.y + eased * comet.length * 0.72;
        const tail = context.createLinearGradient(headX - comet.length, headY - comet.length * 0.4, headX, headY);
        const fade = Math.sin(progress * Math.PI);
        tail.addColorStop(0, 'rgba(245, 139, 77, 0)');
        tail.addColorStop(0.72, `rgba(245, 139, 77, ${fade * 0.13})`);
        tail.addColorStop(1, `rgba(255, 241, 220, ${fade * 0.8})`);
        context.beginPath();
        context.moveTo(headX - comet.length, headY - comet.length * 0.4);
        context.lineTo(headX, headY);
        context.strokeStyle = tail;
        context.lineWidth = 1.2;
        context.stroke();
        context.beginPath();
        context.arc(headX, headY, 1.5 + fade, 0, Math.PI * 2);
        context.fillStyle = `rgba(255, 239, 213, ${fade * 0.86})`;
        context.shadowColor = 'rgba(245, 139, 77, 0.8)';
        context.shadowBlur = 12;
        context.fill();
        context.shadowBlur = 0;
        if (progress >= 1) comet = null;
      }

      if (!motionPreference.matches) frame = window.requestAnimationFrame(draw);
    };

    const onPointerMove = (event) => {
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      pointer.active = true;
      if (motionPreference.matches) draw(0);
    };
    const onPointerLeave = () => { pointer.active = false; };
    const onMotionPreferenceChange = () => {
      window.cancelAnimationFrame(frame);
      comet = null;
      if (motionPreference.matches) draw(0);
      else frame = window.requestAnimationFrame(draw);
    };
    const onVisibilityChange = () => {
      window.cancelAnimationFrame(frame);
      if (!document.hidden && !motionPreference.matches) frame = window.requestAnimationFrame(draw);
    };

    resize();
    if (!motionPreference.matches) frame = window.requestAnimationFrame(draw);
    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('pointerleave', onPointerLeave, { passive: true });
    document.addEventListener('visibilitychange', onVisibilityChange);
    motionPreference.addEventListener('change', onMotionPreferenceChange);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerleave', onPointerLeave);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      motionPreference.removeEventListener('change', onMotionPreferenceChange);
    };
  }, []);

  return <canvas ref={canvasRef} className="space-backdrop" aria-hidden="true" />;
}
