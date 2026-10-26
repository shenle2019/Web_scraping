/*
 * bili_sign.c —— 复刻 day19 的 so 层签名逻辑（仅学习研究使用）
 *
 * 对应课件里的 libbili.so：
 *   - JNI_OnLoad 里 RegisterNatives 动态注册，导出表里看不到 Java_xxx 符号
 *   - 内部 md5_init / md5_update / md5_final，明文一次 update，四段盐各一次 update
 *   - 结果通过 NewStringUTF 交回 Java
 *
 * 为了让 hook 脚本能按「模块基址 + 偏移」定位，md5_update 特意导出为
 * bili_md5_update（真实样本里是静态函数，需要用 IDA 找偏移）。
 */
#include <jni.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    uint32_t state[4];
    uint32_t count[2];
    uint8_t  buffer[64];
} MD5_CTX;

#define F(x, y, z) (((x) & (y)) | (~(x) & (z)))
#define G(x, y, z) (((x) & (z)) | ((y) & ~(z)))
#define H(x, y, z) ((x) ^ (y) ^ (z))
#define I(x, y, z) ((y) ^ ((x) | ~(z)))
#define ROTL(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

#define STEP(f, a, b, c, d, x, t, s) \
    (a) += f((b), (c), (d)) + (x) + (uint32_t)(t); \
    (a) = ROTL((a), (s)); \
    (a) += (b);

static void md5_transform(uint32_t state[4], const uint8_t block[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t x[16];
    int i;
    for (i = 0; i < 16; i++) {
        x[i] = (uint32_t)block[i * 4]
             | ((uint32_t)block[i * 4 + 1] << 8)
             | ((uint32_t)block[i * 4 + 2] << 16)
             | ((uint32_t)block[i * 4 + 3] << 24);
    }

    STEP(F, a, b, c, d, x[0],  0xd76aa478, 7)  STEP(F, d, a, b, c, x[1],  0xe8c7b756, 12)
    STEP(F, c, d, a, b, x[2],  0x242070db, 17) STEP(F, b, c, d, a, x[3],  0xc1bdceee, 22)
    STEP(F, a, b, c, d, x[4],  0xf57c0faf, 7)  STEP(F, d, a, b, c, x[5],  0x4787c62a, 12)
    STEP(F, c, d, a, b, x[6],  0xa8304613, 17) STEP(F, b, c, d, a, x[7],  0xfd469501, 22)
    STEP(F, a, b, c, d, x[8],  0x698098d8, 7)  STEP(F, d, a, b, c, x[9],  0x8b44f7af, 12)
    STEP(F, c, d, a, b, x[10], 0xffff5bb1, 17) STEP(F, b, c, d, a, x[11], 0x895cd7be, 22)
    STEP(F, a, b, c, d, x[12], 0x6b901122, 7)  STEP(F, d, a, b, c, x[13], 0xfd987193, 12)
    STEP(F, c, d, a, b, x[14], 0xa679438e, 17) STEP(F, b, c, d, a, x[15], 0x49b40821, 22)

    STEP(G, a, b, c, d, x[1],  0xf61e2562, 5)  STEP(G, d, a, b, c, x[6],  0xc040b340, 9)
    STEP(G, c, d, a, b, x[11], 0x265e5a51, 14) STEP(G, b, c, d, a, x[0],  0xe9b6c7aa, 20)
    STEP(G, a, b, c, d, x[5],  0xd62f105d, 5)  STEP(G, d, a, b, c, x[10], 0x02441453, 9)
    STEP(G, c, d, a, b, x[15], 0xd8a1e681, 14) STEP(G, b, c, d, a, x[4],  0xe7d3fbc8, 20)
    STEP(G, a, b, c, d, x[9],  0x21e1cde6, 5)  STEP(G, d, a, b, c, x[14], 0xc33707d6, 9)
    STEP(G, c, d, a, b, x[3],  0xf4d50d87, 14) STEP(G, b, c, d, a, x[8],  0x455a14ed, 20)
    STEP(G, a, b, c, d, x[13], 0xa9e3e905, 5)  STEP(G, d, a, b, c, x[2],  0xfcefa3f8, 9)
    STEP(G, c, d, a, b, x[7],  0x676f02d9, 14) STEP(G, b, c, d, a, x[12], 0x8d2a4c8a, 20)

    STEP(H, a, b, c, d, x[5],  0xfffa3942, 4)  STEP(H, d, a, b, c, x[8],  0x8771f681, 11)
    STEP(H, c, d, a, b, x[11], 0x6d9d6122, 16) STEP(H, b, c, d, a, x[14], 0xfde5380c, 23)
    STEP(H, a, b, c, d, x[1],  0xa4beea44, 4)  STEP(H, d, a, b, c, x[4],  0x4bdecfa9, 11)
    STEP(H, c, d, a, b, x[7],  0xf6bb4b60, 16) STEP(H, b, c, d, a, x[10], 0xbebfbc70, 23)
    STEP(H, a, b, c, d, x[13], 0x289b7ec6, 4)  STEP(H, d, a, b, c, x[0],  0xeaa127fa, 11)
    STEP(H, c, d, a, b, x[3],  0xd4ef3085, 16) STEP(H, b, c, d, a, x[6],  0x04881d05, 23)
    STEP(H, a, b, c, d, x[9],  0xd9d4d039, 4)  STEP(H, d, a, b, c, x[12], 0xe6db99e5, 11)
    STEP(H, c, d, a, b, x[15], 0x1fa27cf8, 16) STEP(H, b, c, d, a, x[2],  0xc4ac5665, 23)

    STEP(I, a, b, c, d, x[0],  0xf4292244, 6)  STEP(I, d, a, b, c, x[7],  0x432aff97, 10)
    STEP(I, c, d, a, b, x[14], 0xab9423a7, 15) STEP(I, b, c, d, a, x[5],  0xfc93a039, 21)
    STEP(I, a, b, c, d, x[12], 0x655b59c3, 6)  STEP(I, d, a, b, c, x[3],  0x8f0ccc92, 10)
    STEP(I, c, d, a, b, x[10], 0xffeff47d, 15) STEP(I, b, c, d, a, x[1],  0x85845dd1, 21)
    STEP(I, a, b, c, d, x[8],  0x6fa87e4f, 6)  STEP(I, d, a, b, c, x[15], 0xfe2ce6e0, 10)
    STEP(I, c, d, a, b, x[6],  0xa3014314, 15) STEP(I, b, c, d, a, x[13], 0x4e0811a1, 21)
    STEP(I, a, b, c, d, x[4],  0xf7537e82, 6)  STEP(I, d, a, b, c, x[11], 0xbd3af235, 10)
    STEP(I, c, d, a, b, x[2],  0x2ad7d2bb, 15) STEP(I, b, c, d, a, x[9],  0xeb86d391, 21)

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
}

static void md5_init(MD5_CTX *ctx) {
    ctx->count[0] = 0;
    ctx->count[1] = 0;
    /* 对应课件 sub_227C 里的四个魔数：1732584193, -271733879, -1732584194, 271733878 */
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xefcdab89;
    ctx->state[2] = 0x98badcfe;
    ctx->state[3] = 0x10325476;
}

/* 导出，方便 Frida 按符号/偏移 hook，复刻「hook update 拿盐」的过程。
 * noinline 必须加：否则 -O2 会把它内联进 native_sign，hook 就看不到调用。 */
__attribute__((noinline))
JNIEXPORT void JNICALL
bili_md5_update(MD5_CTX *ctx, const void *data, uint32_t len) {
    const uint8_t *p = (const uint8_t *)data;
    uint32_t index = (ctx->count[0] >> 3) & 0x3F;
    uint32_t i;

    if ((ctx->count[0] += (len << 3)) < (len << 3)) ctx->count[1]++;
    ctx->count[1] += (len >> 29);

    if (index) {
        uint32_t need = 64 - index;
        if (len < need) {
            memcpy(&ctx->buffer[index], p, len);
            return;
        }
        memcpy(&ctx->buffer[index], p, need);
        md5_transform(ctx->state, ctx->buffer);
        p += need;
        len -= need;
    }
    for (i = 0; i + 64 <= len; i += 64) md5_transform(ctx->state, p + i);
    memcpy(ctx->buffer, p + i, len - i);
}

static void md5_final(MD5_CTX *ctx, uint8_t digest[16]) {
    uint8_t padding[64];
    uint8_t bits[8];
    uint32_t i, index, padLen;

    for (i = 0; i < 8; i++) bits[i] = (uint8_t)(ctx->count[i >> 2] >> ((i & 3) << 3));
    index = (ctx->count[0] >> 3) & 0x3F;
    padLen = (index < 56) ? (56 - index) : (120 - index);
    memset(padding, 0, sizeof(padding));
    padding[0] = 0x80;
    bili_md5_update(ctx, padding, padLen);
    bili_md5_update(ctx, bits, 8);
    for (i = 0; i < 4; i++) {
        digest[i * 4]     = (uint8_t)(ctx->state[i]);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i] >> 24);
    }
}

static void md5_hex(const uint8_t digest[16], char out[33]) {
    static const char *hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; i++) {
        out[i * 2]     = hex[(digest[i] >> 4) & 0x0F];
        out[i * 2 + 1] = hex[digest[i] & 0x0F];
    }
    out[32] = 0;
}

/* 四段盐，与课件 hook sub_22B0 拿到的完全一致 */
static const char *SALT1 = "560c52cc";
static const char *SALT2 = "d288fed0";
static const char *SALT3 = "45859ed1";
static const char *SALT4 = "8bffd973";

static jstring native_sign(JNIEnv *env, jclass clazz, jstring jplain) {
    const char *plain;
    MD5_CTX ctx;
    uint8_t digest[16];
    char hex[33];
    jstring result;

    (void)clazz;
    plain = (*env)->GetStringUTFChars(env, jplain, NULL);
    if (plain == NULL) return NULL;

    md5_init(&ctx);
    bili_md5_update(&ctx, plain, (uint32_t)strlen(plain));
    bili_md5_update(&ctx, SALT1, 8);
    bili_md5_update(&ctx, SALT2, 8);
    bili_md5_update(&ctx, SALT3, 8);
    bili_md5_update(&ctx, SALT4, 8);
    md5_final(&ctx, digest);
    md5_hex(digest, hex);

    (*env)->ReleaseStringUTFChars(env, jplain, plain);
    result = (*env)->NewStringUTF(env, hex);
    return result;
}

static const JNINativeMethod kMethods[] = {
    {"nativeSign", "(Ljava/lang/String;)Ljava/lang/String;", (void *)native_sign}
};

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = NULL;
    jclass clazz;
    (void)reserved;

    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK) return -1;
    clazz = (*env)->FindClass(env, "com/example/bililike/BiliSign");
    if (clazz == NULL) return -1;
    if ((*env)->RegisterNatives(env, clazz, kMethods, 1) < 0) return -1;
    return JNI_VERSION_1_6;
}
