import graphene # type: ignore
import graphql_jwt # type: ignore

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello World!")

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
