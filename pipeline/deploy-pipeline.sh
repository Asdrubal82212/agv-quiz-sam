#!/bin/bash
set -e

echo ""
echo "======================================"
echo "  Desplegando CodePipeline en AWS"
echo "======================================"
echo ""

read -p "GitHub Owner (ej: Asdrubal82212):               " GITHUB_OWNER
read -p "GitHub Repo  (ej: agv-quiz-sam):                " GITHUB_REPO
read -p "GitHub Branch (ej: main):                       " GITHUB_BRANCH
read -p "ARN de la conexión GitHub (CodeStar):           " CONNECTION_ARN
read -p "Bucket de artefactos (agv-quiz-sam-artifacts):  " ARTIFACTS_BUCKET
read -p "Email para aprobación de Prod:                  " APPROVAL_EMAIL
read -p "Región AWS (ej: us-east-1):                     " AWS_REGION

STACK_NAME="agv-pipeline-s3"

echo ""
echo "Desplegando stack '$STACK_NAME' en '$AWS_REGION' ..."
echo ""

aws cloudformation deploy \
  --template-file pipeline/pipeline.yaml \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    GitHubOwner="$GITHUB_OWNER" \
    GitHubRepo="$GITHUB_REPO" \
    GitHubBranch="$GITHUB_BRANCH" \
    GitHubConnectionArn="$CONNECTION_ARN" \
    ArtifactsBucket="$ARTIFACTS_BUCKET" \
    ApprovalEmail="$APPROVAL_EMAIL"

echo ""
echo "======================================"
echo "  Pipeline desplegado exitosamente"
echo "======================================"
echo ""

aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='PipelineUrl'].OutputValue" \
  --output text
