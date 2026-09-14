const AWS = require('aws-sdk')

const RESPONSE = require('./lib/response')

const S3 = new AWS.S3()

AWS.config.update({ region: process.env.AWS_REGION })

let indexCache

module.exports.index = async () => {
  try {
    let index = indexCache

    if (!index) {
      index = await getAsset('index.html')
      index.data = replaceCloudFront(index.data, process.env.CLOUDFRONT_DOMAIN)
      indexCache = index
    }

    return RESPONSE.any(index.data, index.contentType)
  } catch (err) {
    console.log('error', err)
    return RESPONSE.error(err)
  }
}

function replaceCloudFront (htmlString, domain) {
  return htmlString.replace(/http:\/\/localhost:8080/g, `https://${domain}`)
}

async function getAsset (assetName) {
  const params = {
    Bucket: process.env.CLIENT_BUCKET,
    Key: assetName
  }

  try {
    const data = await S3.getObject(params).promise()
    const objectData = data.Body.toString()
    return {
      contentType: data.ContentType,
      data: objectData
    }
  } catch (err) {
    throw err
  }
}
