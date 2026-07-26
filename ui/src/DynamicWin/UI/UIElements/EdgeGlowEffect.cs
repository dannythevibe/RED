using DynamicWin.Main;
using DynamicWin.Utils;
using SkiaSharp;
using System;

namespace DynamicWin.UI.UIElements
{
    public class EdgeGlowEffect
    {
        public bool IsActive = false;
        
        private float dashOffsetL;
        private float dashOffsetR;
        
        private float totalLengthL;
        private float totalLengthR;
        
        private float currentBlur = 4f;
        private float currentStroke = 5f;
        private Col currentColor = new Col(255, 30, 66); // #FF1E42
        
        // Simulating audio pulse
        private float audioPulseTimer = 0f;
        private float currentPulseSpeed = 1f;
        
        private float ambientTimer = 0f;
        
        // Vignette Alpha for Viewport Compression Simulation
        private float vignetteAlpha = 0f;

        private SKPath? leftPath;
        private SKPath? rightPath;

        private float lastWidth = 0;
        private float lastHeight = 0;

        public EdgeGlowEffect()
        {
        }

        public void Update(float deltaTime)
        {
            float targetVignette = IsActive ? 0.6f : 0f;
            vignetteAlpha = Mathf.Lerp(vignetteAlpha, targetVignette, deltaTime * 5f);

            if (IsActive)
            {
                dashOffsetL = Mathf.Lerp(dashOffsetL, 0f, deltaTime * 12f);
                dashOffsetR = Mathf.Lerp(dashOffsetR, 0f, deltaTime * 12f);

                if (dashOffsetL < totalLengthL * 0.15f) // Paths are almost met
                {
                    // Ambient color cycling
                    ambientTimer += deltaTime;
                    int colorPhase = (int)(ambientTimer % 3);
                    
                    Col targetColor = colorPhase switch
                    {
                        0 => new Col(255, 30, 66),  // #FF1E42
                        1 => new Col(255, 107, 74), // #FF6B4A
                        _ => new Col(179, 0, 30)    // #B3001E
                    };
                    currentColor = Col.Lerp(currentColor, targetColor, deltaTime * 2f);

                    // Audio Pulse simulation
                    audioPulseTimer += deltaTime;
                    if (audioPulseTimer > currentPulseSpeed)
                    {
                        audioPulseTimer = 0f;
                        currentPulseSpeed = 0.6f + (float)new Random().NextDouble() * 0.9f;
                    }

                    // Sine wave pulse
                    float pulseProgress = audioPulseTimer / currentPulseSpeed;
                    float pulseVal = (float)Math.Sin(pulseProgress * Math.PI); 
                    
                    currentBlur = Mathf.Lerp(4f, 8f, pulseVal);
                    currentStroke = Mathf.Lerp(4f, 9f, pulseVal);
                }
            }
            else
            {
                // Retract
                dashOffsetL = Mathf.Lerp(dashOffsetL, totalLengthL, deltaTime * 15f);
                dashOffsetR = Mathf.Lerp(dashOffsetR, totalLengthR, deltaTime * 15f);
                
                currentColor = Col.Lerp(currentColor, new Col(255, 30, 66), deltaTime * 5f);
                currentBlur = Mathf.Lerp(currentBlur, 4f, deltaTime * 5f);
                currentStroke = Mathf.Lerp(currentStroke, 5f, deltaTime * 5f);
            }
        }

        public void Draw(SKCanvas canvas, float screenWidth, float screenHeight, IslandObject island)
        {
            // Dim vignette effect (Viewport Compression Illusion)
            if (vignetteAlpha > 0.01f)
            {
                // We use a radial gradient from transparent center to dark edges
                using var vignettePaint = new SKPaint
                {
                    Style = SKPaintStyle.Fill
                };
                
                var center = new SKPoint(screenWidth / 2f, screenHeight / 2f);
                var colors = new SKColor[] { 
                    new SKColor(0, 0, 0, 0), 
                    new SKColor(0, 0, 0, (byte)(200 * vignetteAlpha)) 
                };
                
                vignettePaint.Shader = SKShader.CreateRadialGradient(
                    center,
                    Math.Max(screenWidth, screenHeight) / 1.2f,
                    colors,
                    null,
                    SKShaderTileMode.Clamp
                );

                canvas.DrawRect(0, 0, screenWidth, screenHeight, vignettePaint);
            }

            // Only draw glow if active or retracting
            if (!IsActive && dashOffsetL >= totalLengthL - 5f) return;

            if (screenWidth != lastWidth || screenHeight != lastHeight)
            {
                lastWidth = screenWidth;
                lastHeight = screenHeight;

                float r = Math.Max(12, Math.Min(screenWidth * 0.02f, 32f));
                // Flank offset starts slightly inside the island's bounds
                float activeIslandWidth = 220f; // Max expanded width
                float flankOffset = (activeIslandWidth / 2f) - 10f;
                float startXL = (screenWidth / 2f) - flankOffset;
                float startXR = (screenWidth / 2f) + flankOffset;

                leftPath = new SKPath();
                leftPath.MoveTo(startXL, 2f);
                leftPath.LineTo(r, 2f);
                leftPath.QuadTo(2f, 2f, 2f, r);
                leftPath.LineTo(2f, screenHeight - r);
                leftPath.QuadTo(2f, screenHeight - 2f, r, screenHeight - 2f);
                leftPath.LineTo(screenWidth / 2f, screenHeight - 2f);
                
                using var measureL = new SKPathMeasure(leftPath, false);
                totalLengthL = measureL.Length;
                
                rightPath = new SKPath();
                rightPath.MoveTo(startXR, 2f);
                rightPath.LineTo(screenWidth - r, 2f);
                rightPath.QuadTo(screenWidth - 2f, 2f, screenWidth - 2f, r);
                rightPath.LineTo(screenWidth - 2f, screenHeight - r);
                rightPath.QuadTo(screenWidth - 2f, screenHeight - 2f, screenWidth - r, screenHeight - 2f);
                rightPath.LineTo(screenWidth / 2f, screenHeight - 2f);
                
                using var measureR = new SKPathMeasure(rightPath, false);
                totalLengthR = measureR.Length;

                if (!IsActive)
                {
                    dashOffsetL = totalLengthL;
                    dashOffsetR = totalLengthR;
                }
            }

            if (leftPath == null || rightPath == null) return;

            using var glowPaint = new SKPaint
            {
                Style = SKPaintStyle.Stroke,
                StrokeWidth = currentStroke,
                Color = currentColor.Value(),
                IsAntialias = true,
                StrokeCap = SKStrokeCap.Round,
                ImageFilter = SKImageFilter.CreateDropShadow(0, 0, currentBlur, currentBlur, currentColor.Value())
            };

            // Apply dash effect for propagation
            glowPaint.PathEffect = SKPathEffect.CreateDash(new float[] { totalLengthL, totalLengthL }, dashOffsetL);
            canvas.DrawPath(leftPath, glowPaint);

            glowPaint.PathEffect = SKPathEffect.CreateDash(new float[] { totalLengthR, totalLengthR }, dashOffsetR);
            canvas.DrawPath(rightPath, glowPaint);
        }
    }
}
