#include <jni.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/*
 * 复刻课件里的 libJNIEncrypt.so：
 * - JNI_OnLoad 动态注册 getByteValues / encodeByte
 * - getByteValues 返回固定的 0101 串（干扰项）
 * - encodeByte 忽略第二个参数，用固定 key 做 AES-128-ECB/PKCS5 + Base64
 * - 额外导出 AES_128_ECB_PKCS5Padding_Encrypt，方便 Frida 按课件方式 Hook
 *
 * 仅限学习研究，禁止商用。
 */

static const char *FIXED_KEY = "d245a0ba8d678a61";

static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

static uint8_t xtime(uint8_t x) {
    return (uint8_t) ((x << 1) ^ (((x >> 7) & 1) * 0x1b));
}

static void add_round_key(uint8_t *state, const uint8_t *round_key) {
    int i;
    for (i = 0; i < 16; i++) {
        state[i] ^= round_key[i];
    }
}

static void sub_bytes(uint8_t *state) {
    int i;
    for (i = 0; i < 16; i++) {
        state[i] = sbox[state[i]];
    }
}

static void shift_rows(uint8_t *s) {
    uint8_t t;
    t = s[1]; s[1] = s[5]; s[5] = s[9]; s[9] = s[13]; s[13] = t;
    t = s[2]; s[2] = s[10]; s[10] = t;
    t = s[6]; s[6] = s[14]; s[14] = t;
    t = s[15]; s[15] = s[11]; s[11] = s[7]; s[7] = s[3]; s[3] = t;
}

static void mix_columns(uint8_t *s) {
    int i;
    for (i = 0; i < 4; i++) {
        uint8_t *c = s + i * 4;
        uint8_t a = c[0], b = c[1], d = c[2], e = c[3];
        c[0] = (uint8_t) (xtime(a) ^ (xtime(b) ^ b) ^ d ^ e);
        c[1] = (uint8_t) (a ^ xtime(b) ^ (xtime(d) ^ d) ^ e);
        c[2] = (uint8_t) (a ^ b ^ xtime(d) ^ (xtime(e) ^ e));
        c[3] = (uint8_t) ((xtime(a) ^ a) ^ b ^ d ^ xtime(e));
    }
}

static void key_expansion(const uint8_t *key, uint8_t *round_key) {
    int i;
    uint8_t rcon = 1;
    memcpy(round_key, key, 16);
    for (i = 16; i < 176; i += 4) {
        uint8_t t0 = round_key[i - 4];
        uint8_t t1 = round_key[i - 3];
        uint8_t t2 = round_key[i - 2];
        uint8_t t3 = round_key[i - 1];
        if (i % 16 == 0) {
            uint8_t tmp = t0;
            t0 = (uint8_t) (sbox[t1] ^ rcon);
            t1 = sbox[t2];
            t2 = sbox[t3];
            t3 = sbox[tmp];
            rcon = xtime(rcon);
        }
        round_key[i] = (uint8_t) (round_key[i - 16] ^ t0);
        round_key[i + 1] = (uint8_t) (round_key[i - 15] ^ t1);
        round_key[i + 2] = (uint8_t) (round_key[i - 14] ^ t2);
        round_key[i + 3] = (uint8_t) (round_key[i - 13] ^ t3);
    }
}

static void aes_encrypt_block(uint8_t *block, const uint8_t *round_key) {
    int round;
    add_round_key(block, round_key);
    for (round = 1; round < 10; round++) {
        sub_bytes(block);
        shift_rows(block);
        mix_columns(block);
        add_round_key(block, round_key + round * 16);
    }
    sub_bytes(block);
    shift_rows(block);
    add_round_key(block, round_key + 160);
}

static char *base64_encode(const uint8_t *in, int len) {
    static const char tab[] =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    int out_len = 4 * ((len + 2) / 3);
    char *out = (char *) malloc((size_t) out_len + 1);
    int i = 0, j = 0;
    if (out == NULL) {
        return NULL;
    }
    while (i + 2 < len) {
        uint32_t v = ((uint32_t) in[i] << 16) | ((uint32_t) in[i + 1] << 8) | in[i + 2];
        out[j++] = tab[(v >> 18) & 0x3f];
        out[j++] = tab[(v >> 12) & 0x3f];
        out[j++] = tab[(v >> 6) & 0x3f];
        out[j++] = tab[v & 0x3f];
        i += 3;
    }
    if (i < len) {
        uint32_t v = (uint32_t) in[i] << 16;
        int remain = len - i;
        if (remain == 2) {
            v |= (uint32_t) in[i + 1] << 8;
        }
        out[j++] = tab[(v >> 18) & 0x3f];
        out[j++] = tab[(v >> 12) & 0x3f];
        out[j++] = (remain == 2) ? tab[(v >> 6) & 0x3f] : '=';
        out[j++] = '=';
    }
    out[j] = '\0';
    return out;
}

/* 供 Frida 按课件方式 Hook 的导出函数 */
char *AES_128_ECB_PKCS5Padding_Encrypt(const char *data, const char *key) {
    int len = (int) strlen(data);
    int pad_len = 16 - (len % 16);
    int total = len + pad_len;
    uint8_t *buf = (uint8_t *) malloc((size_t) total);
    uint8_t round_key[176];
    int offset;
    char *out;
    if (buf == NULL) {
        return NULL;
    }
    memcpy(buf, data, (size_t) len);
    memset(buf + len, pad_len, (size_t) pad_len);
    key_expansion((const uint8_t *) key, round_key);
    for (offset = 0; offset < total; offset += 16) {
        aes_encrypt_block(buf + offset, round_key);
    }
    out = base64_encode(buf, total);
    free(buf);
    return out;
}

static jstring native_get_byte_values(JNIEnv *env, jclass clazz) {
    (void) clazz;
    /* 固定干扰串，与课件一致：Java 层会逐位取反后传给 encodeByte */
    return (*env)->NewStringUTF(env, "0110100101101001011010010110100101101001011010010110100101101001");
}

static jstring native_encode_byte(JNIEnv *env, jclass clazz, jbyteArray data, jstring mask) {
    jsize len;
    jbyte *bytes;
    char *plain;
    char *out;
    jstring result;
    (void) clazz;
    (void) mask; /* 与课件一致：第二个参数不参与加密 */

    len = (*env)->GetArrayLength(env, data);
    bytes = (*env)->GetByteArrayElements(env, data, NULL);
    plain = (char *) malloc((size_t) len + 1);
    if (plain == NULL) {
        return NULL;
    }
    memcpy(plain, bytes, (size_t) len);
    plain[len] = '\0';
    (*env)->ReleaseByteArrayElements(env, data, bytes, JNI_ABORT);

    out = AES_128_ECB_PKCS5Padding_Encrypt(plain, FIXED_KEY);
    free(plain);
    if (out == NULL) {
        return NULL;
    }
    result = (*env)->NewStringUTF(env, out);
    free(out);
    return result;
}

static const JNINativeMethod gMethods[] = {
        {"getByteValues", "()Ljava/lang/String;",                   (void *) native_get_byte_values},
        {"encodeByte",    "([BLjava/lang/String;)Ljava/lang/String;", (void *) native_encode_byte}
};

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = NULL;
    jclass clazz;
    (void) reserved;

    if ((*vm)->GetEnv(vm, (void **) &env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }
    clazz = (*env)->FindClass(env, "com/repl/dewu/security/AESEncrypt");
    if (clazz == NULL) {
        return JNI_ERR;
    }
    if ((*env)->RegisterNatives(env, clazz, gMethods, 2) < 0) {
        return JNI_ERR;
    }
    return JNI_VERSION_1_6;
}
