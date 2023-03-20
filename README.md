# ChatGPT-Bot
Discordと連携し、ChatBotとして動作するプログラムです。
動作には改善の余地がありますが、とりあえず動作するはずです。

## 操作方法
Discordチャンネル上の入力で動作します。


!chat listen でチャンネルにおける応答許可を与え、!chat a / @mention のどちらかで応答させます。

過去の会話は800トークン、もしくは!splitのみの投稿が検出されるまで読み込みます。会話文として認識しない投稿は「!」や「誰かへのメンション」で始まる文章です。

これにより、!で始まる他のBotの投稿や下記の1問1答形式の投稿を読み取らず、文脈を維持したまま会話を続行することができます。

@mention 質問文　の形式で投稿することで、質問への回答を得ることができます。これは過去の履歴を一切読み込まないため、トークンの節約に有効です。

キャラクターを模倣するプロンプトや各種のプロンプトを導入したい場合、各種設定を一括で適用したい場合はキャラクター設定の説明に従って設定ファイルを作成してください。
!chat chara <設定ファイルの名前:拡張子無し>

## 環境設定
.envファイルを各自で作成してください。

DISCORD DEVELOPER PORTAL(https://discord.com/developers/applications )で新規アプリケーションを作成し、Botユーザーを登録してください。Botユーザーの管理画面からTokenを入手し

DISCORD_API_KEY="Token"

のように記述してください。 SCOPES [Bot] 権限 [Send Messages,Read Message history] でURLを生成し、Botユーザーを使いたいサーバーに招待してください。
                 
OpenAI(https://platform.openai.com/ )でAPI_KEYを入手し

OPENAI_API_KEY="API_KEY"

のように記述してください。

## キャラクター設定

3/20にファイルのフォーマットを変更しました。旧来のフォーマットを読み込ませると不具合を引き起こす可能性があります。

Json形式に対応しています。以下のテンプレートに従って作成してください。

```
{"system_message":[
　　{
      "role":　"system",
      "content":　"あなたは役に立つアシスタントです"
    }
  ],
  "temp": 0.5,
  "receive_token": 500,
  "send_token": 800,
  "send_user_name": true,
  "messages_preloaded": 200
}
```
system_messageはAPIに最初に与えるメッセージです。これに市販のpromptを流し込むことで試すことができます。"role":"system"に限らず、自由に編集してください。

tempはAPIのtemperatureに、receive_tokenはmax_tokensに対応します。

send_user_nameは入力文字列に発言したユーザー名を含めるかどうかのフラグです。trueの場合、Aというユーザーがこんにちはと投稿した場合、"A「こんにちは」"のように変換します。
猫語変換のような変換を行うpromptを適用する場合はfalse、対話型のpromptを適用する場合はtrueを推奨します。

send_tokenは会話履歴の読み込みtoken数です。messages_preloadedは会話履歴の読み込み投稿数です。変換を行うpromptの場合は2に設定することを推奨します。（直前の応答指示とその前の変換前文字列で2投稿になります）対話型のpromptの場合、100以上の値を推奨します。

なお、send_tokenとmessages_preloadedではsend_tokenが優先されます。send_token以上の投稿が直前にある場合、いかなる投稿も読まれません。（仕様です）

## 更新計画
変換を行う専用のコマンドを実装する予定です。また、小説のメモ->プロット->短編のように、複数の変換を順次適用するパイプライン機能も実装予定です。
