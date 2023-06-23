function create_canvas(textList, label){
    var canvas = document.getElementById('textCanvas');
    var ctx = canvas.getContext('2d');
    var canvasContainer = $('.canvas-container');
    
    var containerWidth = canvasContainer.width();
    var containerHeight = canvasContainer.height();
    canvas.width = containerWidth;
    canvas.height = containerHeight;

    // 캔버스 그리기
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    class TextElement {
        constructor(text, x, y, width, height) {
            this.text = text;
            this.x = x;
            this.y = y+parseInt(ctx.font); // y와 height는 반대
            this.width = width;
            this.height = height;
            this.speedX = Math.random() * 2 - 1; // X축 이동 속도
            this.speedY = Math.random() * 2 - 1; // Y축 이동 속도
        }
        
        update() {
            if(!this.isStopped){
                this.x += this.speedX;
                this.y += this.speedY;
            }

            if (this.x < 0 || this.x+this.width > canvas.width) {
                this.speedX *= -1;
            }
            if (this.y-this.height < 0 || this.y+this.height > canvas.height) {
                this.speedY *= -1;
            }
            for (let i = 0; i < textElements.length; i++) {
                const otherElement = textElements[i];
                if (otherElement !== this) {
                    if (this.x < otherElement.x + otherElement.width &&
                        this.x + this.width > otherElement.x && 
                        this.y > otherElement.y - otherElement.height &&
                        this.y - this.height < otherElement.y) {
                        this.speedX *= -1;
                        otherElement.speedX *= -1;
                        this.speedY *= -1;
                        otherElement.speedY *= -1;
                    }
                }
            }
        }   
        draw() {
            ctx.fillText(this.text, this.x, this.y);
        }
        stop() {
            this.isStopped = true;
        }

        resume() {
            this.isStopped = false;
        }
    }
    var texts = textList;
    var textElements = [];

    // 텍스트 스타일 설정
    var fontSize = Math.min(containerWidth, containerHeight) / 20;
    ctx.font = fontSize + 'px Arial';
    ctx.fillStyle = '#000';

    // 텍스트 그리기
    for (var i = 0; i < texts.length; i++) {
        var text = texts[i];
        var textWidth = ctx.measureText(text).width;
        var textHeight = parseInt(ctx.font)
        var textX = Math.random() * (containerWidth - textWidth);
        var textY = Math.random() * (containerHeight - textHeight);
        var textElement = new TextElement(text, textX, textY, textWidth, textHeight);
        textElements.push(textElement);
        ctx.fillText(text, textX, textY);
    }

    animate();

// 애니메이션 루프 함수
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 각 텍스트 요소 업데이트 및 그리기
    for (let i = 0; i < textElements.length; i++) {
        const textElement = textElements[i];
        textElement.update();
        textElement.draw();
    }
    requestAnimationFrame(animate);

}
function drawTextElements() {
    for (let i = 0; i < textElements.length; i++) {
        const textElement = textElements[i];
        ctx.font = `${textElement.scale * textElement.height}px Arial`; // 크기 조정된 텍스트 크기 설정
        ctx.fillText(textElement.text, textElement.x, textElement.y);
    }
}
function animate_select_text(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawTextElements();
    requestAnimationFrame(animate_select_text);
}
  canvas.addEventListener('mousemove', function(event) {
	canvas.style.cursor = 'default'
    const mouseX = event.offsetX;
    const mouseY = event.offsetY;

    for (let i = 0; i < texts.length; i++) {
        const textElement = textElements[i];

        // 텍스트의 경계 영역 계산
        const textLeft = textElement.x;
        const textRight = textElement.x + textElement.width;
        const textTop = textElement.y - textElement.height;
        const textBottom = textElement.y;

        // 마우스 좌표와 텍스트 경계 영역 비교
        if (
            mouseX >= textLeft &&
            mouseX <= textRight &&
            mouseY >= textTop &&
            mouseY <= textBottom
        ) {
			canvas.style.cursor = 'pointer'
            textElement.stop();
            textElement.scale = 1.2;
            animate_select_text();
        } else {
            textElement.resume();
            textElement.scale = 1.0;

        }
    }
});
canvas.addEventListener('click', function(event) {
    const mouseX = event.offsetX;
    const mouseY = event.offsetY;

    // 텍스트 요소 선택
    for (let i = 0; i < textElements.length; i++) {
        const textElement = textElements[i];

        // 텍스트의 경계 영역 계산
        const textLeft = textElement.x;
        const textRight = textElement.x + textElement.width;
        const textTop = textElement.y - textElement.height;
        const textBottom = textElement.y;

        // 마우스 좌표와 텍스트 경계 영역 비교
        if (
            mouseX >= textLeft &&
            mouseX <= textRight &&
            mouseY >= textTop &&
            mouseY <= textBottom
        ) {
            // 새로운 페이지로 이동
            window.location.href = `/main/${label}/${textElements[i].text}#home`;
            break;
        }
    }
});
}

  