import sharp from 'sharp'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { mkdirSync, existsSync } from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const sizes = [72, 96, 128, 144, 152, 192, 384, 512]
const iconsDir = join(__dirname, '../public/icons')
const svgPath = join(iconsDir, 'icon.svg')

// 确保目录存在
if (!existsSync(iconsDir)) {
  mkdirSync(iconsDir, { recursive: true })
}

async function generateIcons() {
  console.log('开始生成 PNG 图标...')

  for (const size of sizes) {
    const outputPath = join(iconsDir, `icon-${size}.png`)
    try {
      await sharp(svgPath)
        .resize(size, size)
        .png()
        .toFile(outputPath)
      console.log(`✓ 生成 icon-${size}.png`)
    } catch (error) {
      console.error(`✗ 生成 icon-${size}.png 失败:`, error.message)
    }
  }

  console.log('图标生成完成!')
}

generateIcons()
