<script setup>
import { computed, onMounted, ref } from 'vue';

const apiBase = import.meta.env.VITE_API_BASE || '';

const file = ref(null);
const previewUrl = ref('');
const model = ref(null);
const result = ref(null);
const error = ref('');
const loading = ref(false);
const frameCount = ref(24);
const selectedThumbIndex = ref(2);
const thumbnails = ref([]);

const predictions = computed(() => result.value?.predictions ?? []);
const topPrediction = computed(() => predictions.value[0] ?? null);
const hasVideo = computed(() => Boolean(file.value && previewUrl.value));
const hasFrames = computed(() => thumbnails.value.length > 0);
const hasResult = computed(() => predictions.value.length > 0);
const modelReady = computed(() => Boolean(model.value?.ready));
const currentFrame = computed(() => thumbnails.value[selectedThumbIndex.value]?.frame ?? 16);
const currentFrameImage = computed(() => thumbnails.value[selectedThumbIndex.value]?.image ?? '');

const statusText = computed(() => {
  if (loading.value) return '识别中';
  if (hasResult.value) return '识别成功';
  if (hasVideo.value) return '已抽帧';
  return modelReady.value ? '模型就绪' : '等待模型';
});

const actionDisabled = computed(() => !file.value || loading.value || !modelReady.value);
const actionTitle = computed(() => {
  if (!file.value) return '请先上传视频';
  if (!modelReady.value) return model.value?.message || '模型环境未就绪';
  return '调用后端模型识别';
});

async function refreshModel() {
  try {
    const response = await fetch(`${apiBase}/api/model`);
    model.value = await response.json();
  } catch {
    model.value = null;
  }
}

function onFileChange(event) {
  const nextFile = event.target.files?.[0];
  file.value = nextFile || null;
  result.value = null;
  error.value = '';
  thumbnails.value = [];
  selectedThumbIndex.value = 2;

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = nextFile ? URL.createObjectURL(nextFile) : '';
  if (previewUrl.value) extractThumbnails(previewUrl.value);
}

async function submit() {
  if (!file.value) return;

  loading.value = true;
  error.value = '';
  result.value = null;

  const formData = new FormData();
  formData.append('file', file.value);

  try {
    const response = await fetch(`${apiBase}/api/predict?top_k=3`, {
      method: 'POST',
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || '识别失败');
    result.value = payload;
    model.value = payload.model;
  } catch (err) {
    error.value = err.message;
    await refreshModel();
  } finally {
    loading.value = false;
  }
}

function resetDemo() {
  file.value = null;
  result.value = null;
  error.value = '';
  thumbnails.value = [];
  selectedThumbIndex.value = 2;
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = '';
}

function extractThumbnails(src) {
  const video = document.createElement('video');
  video.src = src;
  video.muted = true;
  video.preload = 'metadata';
  video.crossOrigin = 'anonymous';

  video.onloadedmetadata = async () => {
    const duration = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : 2;
    const ratios = [0.06, 0.34, 0.66, 0.94];
    const frames = [];

    for (let index = 0; index < ratios.length; index += 1) {
      const frame = Math.min(frameCount.value, index * 7 + 1);
      const time = Math.max(duration * ratios[index], 0.01);
      const image = await captureFrame(video, time);
      frames.push({ image, frame, label: `第 ${frame} 帧` });
    }

    thumbnails.value = frames;
    selectedThumbIndex.value = Math.min(2, frames.length - 1);
  };
}

function captureFrame(video, time) {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    const finish = () => {
      canvas.width = 640;
      canvas.height = 360;
      const context = canvas.getContext('2d');
      context.fillStyle = '#010102';
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      resolve(canvas.toDataURL('image/jpeg', 0.86));
    };
    video.onseeked = finish;
    video.currentTime = Math.min(time, Math.max(video.duration - 0.05, 0.01));
  });
}

onMounted(refreshModel);
</script>

<template>
  <main class="page-shell">
    <section class="hero-band">
      <div>
        <h1>动态手势识别答辩演示台</h1>
        <p>基于 RGB 视频时序分类的离线演示页面，同步展示关键帧、概率排序与最终识别结果。</p>
        <div class="hero-tags">
          <span>RGB 时序分类</span>
          <span>Jester 27 类</span>
          <span>离线演示闭环</span>
        </div>
      </div>
      <div class="success-pill" :class="{ muted: !hasResult }">
        <i></i>
        {{ statusText }}
      </div>
    </section>

    <section class="dashboard-grid">
      <aside class="panel upload-panel">
        <p class="section-kicker">演示入口</p>
        <h2>上传视频并开始识别</h2>
        <p class="muted-text">上传标准手势视频后，系统会抽取代表帧并调用 TSM R50 模型完成离线识别。</p>

        <div class="metric-grid">
          <div>
            <span>默认模型</span>
            <strong>TSM R50</strong>
          </div>
          <div>
            <span>动作类别</span>
            <strong>27 类</strong>
          </div>
          <div>
            <span>当前抽帧</span>
            <strong>{{ frameCount }} 帧</strong>
          </div>
        </div>

        <label class="file-box">
          <input type="file" accept="video/*" @change="onFileChange" />
          <span>上传视频</span>
          <strong>{{ file?.name || '选择演示视频' }}</strong>
          <em>{{ file ? '重新选择' : '选择文件' }}</em>
        </label>

        <div class="video-card">
          <video v-if="previewUrl" :src="previewUrl" controls />
          <div v-else class="video-empty">等待视频</div>
          <p>{{ file?.name || '未选择视频' }}</p>
        </div>

        <label class="input-label" for="frame-count">抽帧数量</label>
        <input id="frame-count" v-model.number="frameCount" class="frame-input" type="number" min="8" max="64" />

        <p v-if="file && !modelReady" class="model-warning">{{ model?.message || '模型环境未就绪，暂不能执行真实识别。' }}</p>

        <button class="primary-button" type="button" :disabled="actionDisabled" :title="actionTitle" @click="submit">
          {{ loading ? '正在识别...' : '开始识别' }}
        </button>
        <button class="ghost-button" type="button" @click="resetDemo">重置</button>
      </aside>

      <section class="panel process-panel">
        <div class="panel-title-row">
          <div>
            <p class="section-kicker">主展示画面</p>
            <h2>RGB 识别过程</h2>
          </div>
          <span class="mode-pill">离线识别</span>
        </div>

        <div class="main-frame">
          <img v-if="currentFrameImage" :src="currentFrameImage" alt="当前抽帧" />
          <div v-else class="frame-placeholder">上传视频后显示抽取出的 RGB 帧</div>
          <span v-if="hasFrames" class="frame-index">第 {{ currentFrame }} 帧</span>
          <span class="frame-chip">RGB 原图</span>
        </div>

        <div class="timeline-row">
          <span>当前帧 <strong>{{ hasFrames ? `第 ${currentFrame} 帧` : '等待抽帧' }}</strong></span>
          <span>画面模式 <strong>RGB 视频帧</strong></span>
          <span>过程说明 <strong>{{ hasFrames ? '展示动作变化' : '上传后生成' }}</strong></span>
        </div>

        <div class="thumb-section">
          <div class="thumb-head">
            <strong>识别过程</strong>
            <span>展示模型参考的代表帧变化</span>
          </div>
          <div class="thumb-grid">
            <button
              v-for="(thumb, index) in thumbnails"
              :key="thumb.label"
              type="button"
              class="thumb-card"
              :class="{ active: selectedThumbIndex === index }"
              @click="selectedThumbIndex = index"
            >
              <img :src="thumb.image" alt="" />
              <span>{{ thumb.label }}</span>
            </button>
            <div v-if="!thumbnails.length" class="thumb-empty">上传后生成关键帧</div>
          </div>
        </div>
      </section>

      <aside class="panel result-panel">
        <div class="panel-title-row">
          <div>
            <p class="section-kicker">最终输出</p>
            <h2>手势识别结果</h2>
          </div>
          <span class="mode-pill">Jester 27 类</span>
        </div>

        <div v-if="error" class="error-box">{{ error }}</div>

        <section v-if="topPrediction" class="result-summary">
          <div>
            <span>识别类别</span>
            <strong>{{ topPrediction.label }}</strong>
          </div>
          <div>
            <span>识别置信度</span>
            <strong>{{ (topPrediction.score * 100).toFixed(1) }}%</strong>
          </div>
        </section>
        <section v-else class="result-empty">
          <span>识别类别</span>
          <strong>等待识别</strong>
          <p>上传视频并点击“开始识别”后显示最终类别与置信度。</p>
        </section>

        <div v-if="topPrediction" class="confidence-track">
          <i :style="{ width: `${Math.max(topPrediction.score * 100, 4)}%` }"></i>
        </div>

        <div class="flow-box">
          <span>模型输入<br><strong>RGB 视频帧序列</strong></span>
          <b>→</b>
          <span>时序建模<br><strong>TSM R50</strong></span>
          <b>→</b>
          <span>模型输出<br><strong>最终识别结果</strong></span>
        </div>

        <div class="ranking-head">
          <strong>Top-3 候选结果</strong>
          <span>展示模型对 27 类动作的概率排序</span>
        </div>

        <div v-if="predictions.length" class="rank-list">
          <div v-for="(item, index) in predictions.slice(0, 3)" :key="item.label" class="rank-item">
            <div>
              <strong>{{ index + 1 }}. {{ item.label }}</strong>
              <span>{{ (item.score * 100).toFixed(1) }}%</span>
            </div>
            <i :style="{ width: `${Math.max(item.score * 100, 1)}%` }"></i>
          </div>
        </div>
        <div v-else class="rank-empty">等待模型返回 Top-3 概率排序</div>

        <dl class="detail-list">
          <div>
            <dt>识别状态</dt>
            <dd>{{ result ? '已完成' : '等待识别' }}</dd>
          </div>
          <div>
            <dt>演示视频</dt>
            <dd>{{ file?.name || '未选择视频' }}</dd>
          </div>
          <div>
            <dt>当前视图</dt>
            <dd>{{ hasFrames ? `RGB 第 ${currentFrame} 帧` : '等待抽帧' }}</dd>
          </div>
        </dl>

        <section class="model-notes">
          <div class="notes-head">
            <span>识别参数说明</span>
            <em>RGB 视频</em>
          </div>
          <div class="note-grid">
            <div><span>类别范围</span><strong>Jester 27 类</strong></div>
            <div><span>视频模式</span><strong>RGB 时序识别</strong></div>
            <div><span>特征维度</span><strong>2048</strong></div>
            <div><span>序列长度</span><strong>8</strong></div>
            <div><span>参考准确率</span><strong>96.29%</strong></div>
            <div><span>宏平均 F1</span><strong>95.88%</strong></div>
          </div>
        </section>
      </aside>
    </section>
  </main>
</template>
